from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from MoBook.settings import BASE_URL
from chat.models import Chat, ChatType
from message.models import Message, M2M
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
def transmit_separate(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    target_list = params.get('tar_list')
    message_list = params.get('message_list')
    org_id = params.get('org_id')
    nickname = first_or_default(UserOrganizationProfile, user_id=user.id, org_id=org_id).nickname
    avatar = get_avatar_url("user", user.avatar)
    for chat_id in target_list:
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
            copy.is_record = message.is_record
            if message.file is not None and message.file.name is not None and message.file.name != "":
                copy.file = message.file  # 组合方式
                copy.text = copy.file.name  # 本名
                copy.type = 1  # TODO: 预留，只作为区分
                copy.save()
                response['content'] = copy.file.name
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
            async_to_sync(channel_layer.group_send)(str(chat.id), {
                'type': 'chat_message',
                'data': response
            })

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def transmit_combined(request):
    # 返回mid列表or简略，需要返回一个键，标志为聊天记录，前端自己搓，点进去后前端请求详细信息
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    target_list = params.get('tar_list')
    message_list = params.get('message_list')
    org_id = params.get('org_id')
    nickname = first_or_default(UserOrganizationProfile, user_id=user.id, org_id=org_id).nickname
    avatar = get_avatar_url("user", user.avatar)
    for chat_id in target_list:
        chat = first_or_default(Chat, id=chat_id)
        response = {
            "senderId": user.id,
            "username": nickname,  # 传过来团队内昵称
            "avatar": avatar,  # TODO: 可以前端存储
            "saved": True,
            "distributed": True,
            "seen": True,
            "son_list": message_list,
        }
        message = Message(src_id=user.id, chat_id=chat_id)
        message.is_record = 1
        if chat.type == ChatType.PRIVATE:
            user1_id = UserChatRelation.objects.filter(chat_id=chat_id)[0].user_id
            user2_id = UserChatRelation.objects.filter(chat_id=chat_id)[1].user_id
            nickname1 = first_or_default(UserOrganizationProfile, user_id=user1_id, org_id=org_id).nickname
            nickname2 = first_or_default(UserOrganizationProfile, user_id=user2_id, org_id=org_id).nickname
            message.text = nickname1 + "和" + nickname2 + "的聊天记录"
        else:
            message.text = chat.chat_name + "的聊天记录"
        message.save()


        for son in message_list:
            m2m = M2M(father=message, son=son)
            m2m.save()

        # 更新最新消息
        chat.latest_message = message.id
        chat.save()

        # 更新未读信息数目
        for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
            user_chat_relation.unread += 1
            user_chat_relation.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(str(chat.id), {
            'type': 'chat_message',
            'data': response
        })

    return OkResponse(OkDto())
