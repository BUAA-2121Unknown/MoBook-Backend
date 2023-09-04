from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer, channel_layers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from MoBook.settings import BASE_URL
from chat.consumers import ChatsConsumer
from chat.models import Chat, ChatType, ChatAvatar
from chat.utils.chat_manager import _get_chat_members
from chat.utils.message_manager import pull_message
from message.models import Message, M2M, MessageType
from org.models import Organization
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto
from shared.response.json_response import UnauthorizedResponse, OkResponse
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.time_utils import get_time, get_date
from user.models import User, UserChatRelation, UserOrganizationProfile


@api_view(['POST'])
@csrf_exempt
def transmit(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    target_list = params.get('tar_list')
    message_list = params.get('message_list')
    org_id = params.get('org_id')
    org = first_or_default(Organization, id=org_id)

    nickname = first_or_default(UserOrganizationProfile, user_id=user.id, org_id=org_id).nickname
    avatar = get_avatar_url("user", user.avatar)
    choice = params.get('choice')

    if choice == "separate":
        for chat_id in target_list:
            # print(chat_id)
            chat = first_or_default(Chat, id=chat_id)
            for message_id in message_list:
                message = first_or_default(Message, id=message_id)
                response = {
                    "senderId": user.id,
                    "username": nickname,  # 传过来团队内昵称
                    "avatar": avatar,  # TODO: 可以前端存储
                    "saved": True,
                    "distributed": True,
                    "seen": True,

                }

                copy = Message(src_id=user.id, chat_id=chat_id)
                copy.type = message.type
                copy.is_record = message.is_record
                if message.file is not None and message.file.name is not None and message.file.name != "":
                    copy.file = message.file  # 组合方式
                    copy.text = copy.file.name  # 本名
                      # TODO: 预留，只作为区分
                    copy.save()
                    response['content'] = ""
                    response["files"] = []
                    response['files'].append({
                        "name": copy.file.name,
                        "size": 0,  # TODO: 预留
                        "type": copy.file.name.split('.')[-1],
                        "audio": False,  # TODO: 预留
                        "duration": 0,  # TODO: 预留
                        "url": BASE_URL + copy.file.url,
                        # preview
                        # "progress": 100,  # TODO: 预留
                    })
                text = message.text
                if text is not None:
                    copy.text = text
                    copy.type = 0
                    response['content'] = text
                    copy.save()
                response.update({
                    "_id": copy.id,
                    "indexId": 0,  # TODO: 预留
                    "timestamp": get_time(copy.timestamp),
                    "date": get_date(copy.timestamp),
                })

                # 更新最新消息
                chat.latest_message = copy.id
                chat.save()

                # 更新未读信息数目
                for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
                    user_chat_relation.unread += 1
                    user_chat_relation.save()


                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)("chat" + str(chat.id), {
                    'type': 'chat_message',
                    'data': response
                })

                for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id, org_id=org_id):
                    tmp = {
                        "roomId": chat.id,

                        "roomName": chat.chat_name,
                        "unreadCount": user_chat_relation.unread,
                    }
                    if chat.type == ChatType.ORG:
                        tmp["avatar"] = get_avatar_url("org", org.avatar)
                    elif chat.type == ChatType.PUBLIC:
                        tmp["avatar"] = BASE_URL + ChatAvatar.DEFAULT
                    else:  # 另外一个人的头像
                        for uc in UserChatRelation.objects.filter(chat_id=chat_id):
                            if uc.user_id != user.id:
                                tmp["avatar"] = get_avatar_url("user", first_or_default(User, id=uc.user_id).avatar)
                                tmp["roomName"] = first_or_default(UserOrganizationProfile, user_id=uc.user_id,
                                                                   org_id=org_id).nickname
                    tmp.update({"lastMessage": {
                        "content": message.text,
                        "senderId": str(message.src_id),  # ?
                        "username": nickname,
                        "timestamp": get_time(message.timestamp),
                        "date": get_date(message.timestamp),

                        "saved": True,
                        "distributed": True,
                        "seen": True,
                    }})

                    tmp.update({"users": [],
                                "messages": [],
                                "index": chat.latest_message
                                })


                    chats_channel_layer = channel_layers[ChatsConsumer.channel_layer_alias]
                    async_to_sync(chats_channel_layer.group_send)(
                        "chats" + str(user_chat_relation.user_id) + str(org_id),
                        {
                            "type": "chats",
                            "room": tmp
                        }
                    )
    else:
        for chat_id in target_list:
            chat = first_or_default(Chat, id=chat_id)
            response = {
                "senderId": user.id,
                "content": "",
                "username": nickname,  # 传过来团队内昵称
                "avatar": avatar,  # TODO: 可以前端存储
                "saved": True,
                "distributed": True,
                "seen": True,
                "files": []
            }

            message = Message(src_id=user.id, chat_id=chat_id)
            message.is_record = 1
            message.type = MessageType.RECORD
            if chat.type == ChatType.PRIVATE:
                user1_id = UserChatRelation.objects.filter(chat_id=chat_id)[0].user_id
                user2_id = UserChatRelation.objects.filter(chat_id=chat_id)[1].user_id
                nickname1 = first_or_default(UserOrganizationProfile, user_id=user1_id, org_id=org_id).nickname
                nickname2 = first_or_default(UserOrganizationProfile, user_id=user2_id, org_id=org_id).nickname
                message.text = nickname1 + "和" + nickname2 + "的聊天记录"
            else:
                message.text = chat.chat_name + "的聊天记录"

            message.save()
            response["files"].append({
                "name": "聊天记录",
                "size": 0,  # TODO: 预留
                "type": "docx",
                "audio": False,  # TODO: 预留
                "duration": 0,  # TODO: 预留
                "son_list": message_list,
                "url": ""
            })
            for son in message_list:
                m2m = M2M(father=message.id, son=son)
                m2m.save()

            # 更新最新消息
            chat.latest_message = message.id
            chat.save()

            # 更新未读信息数目
            for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
                user_chat_relation.unread += 1
                user_chat_relation.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("chat" + str(chat.id), {
                'type': 'chat_message',
                'data': response
            })
            for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id, org_id=org_id):
                tmp = {
                    "roomId": chat.id,
                    "roomName": chat.chat_name,
                    "unreadCount": user_chat_relation.unread,
                }
                if chat.type == ChatType.ORG:
                    tmp["avatar"] = get_avatar_url("org", org.avatar)
                elif chat.type == ChatType.PUBLIC:
                    tmp["avatar"] = BASE_URL + ChatAvatar.DEFAULT
                else:  # 另外一个人的头像
                    for uc in UserChatRelation.objects.filter(chat_id=chat_id):
                        if uc.user_id != user.id:
                            tmp["avatar"] = get_avatar_url("user", first_or_default(User, id=uc.user_id).avatar)
                            tmp["roomName"] = first_or_default(UserOrganizationProfile, user_id=uc.user_id,
                                                               org_id=org_id).nickname
                tmp.update({"lastMessage": {
                    "content": message.text,
                    "senderId": str(message.src_id),  # ?
                    "username": nickname,
                    "timestamp": get_time(message.timestamp),
                    "date": get_date(message.timestamp),

                    "saved": True,
                    "distributed": True,
                    "seen": True,
                }})

                tmp.update({"users": [],
                            "messages": [],
                            "index": chat.latest_message
                            })

                chats_channel_layer = channel_layers[ChatsConsumer.channel_layer_alias]
                async_to_sync(chats_channel_layer.group_send)(
                    "chats" + str(user_chat_relation.user_id) + str(org_id),
                    {
                        "type": "chats",
                        "room": tmp
                    }
                )
    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def get_record_content(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    message_id_list = params.get('son_list')
    org_id = params.get('org_id')
    data = {"message_list": []}
    message_list = []
    for message_id in message_id_list:
        message_list.append(first_or_default(Message, id=message_id))
    for message in message_list:
        user_organization_profile = first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                                     org_id=org_id)
        if user_organization_profile is not None:
            nickname = user_organization_profile.nickname
        else:
            nickname = ""
        tmp = {
            "messageId": message.id,
            "message_type": message.type,
            "avatar": get_avatar_url("user", first_or_default(User, id=message.src_id).avatar),  # ?
            "name": nickname,
            "time": get_date(message.timestamp) + " " + get_time(message.timestamp),
        }
        if message.type == 0:
            tmp["content"] = message.text
        elif message.type == 1:
            tmp["image"] = BASE_URL + message.file.url
        elif message.type == 2:
            tmp["src"] = BASE_URL + message.file.url
        elif message.type == 3:
            tmp['filename'] = message.text
            tmp["fileUrl"] = BASE_URL + message.file.url
        else:
            tmp["content"] = message.text
            tmp["son_list"] = [m2m.son for m2m in M2M.objects.filter(father=message.id)]
        data["message_list"].append(tmp)

# # <<<<<<< HEAD
#         for son in message_list:
#             m2m = M2M(father=message, son=son)
#             m2m.save()
#
#         # 更新最新消息
#         chat.latest_message = message.id
#         chat.save()
#
#         # 更新未读信息数目
#         for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
#             user_chat_relation.unread += 1
#             user_chat_relation.save()
#
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(str(chat.id), {
#             'type': 'chat_message',
#             'data': response
#         })
#
#     return OkResponse(OkDto())
# # =======
    return OkResponse(OkDto(data=data))
# >>>>>>> zdw
