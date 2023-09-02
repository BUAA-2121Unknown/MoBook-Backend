from asgiref.sync import async_to_sync
from channels.layers import channel_layers

from MoBook.settings import BASE_URL
from chat.consumers import ChatsConsumer, ChatMessageConsumer
from chat.models import ChatType, ChatAvatar
from chat.utils.chat_manager import _get_chat_members
from message.models import Message, M2M, MessageType
from notif.dtos.notif_payload import NotifAtPayload
from notif.utils.notif_manager import dispatch_notification
from shared.utils.dir_utils import get_avatar_path, get_avatar_url
from shared.utils.file.file_handler import parse_filename
from shared.utils.model.model_extension import first_or_default
from shared.utils.time_utils import get_time, get_date
from user.models import UserChatRelation, UserChatJump, UserOrganizationProfile, User


# TODO: pull older
def new_to_chat(user, chat_id, message_num, org_id):
    data = {"message_list": pull_older(chat_id, message_num, org_id), "at_message_list": get_at_list(user, chat_id)}
    # TODO: 多套了一层
    return data


def new_to_chat_ver1(user, chat_id, org_id):
    data = pull_all(chat_id, org_id)
    user_chat_relation = first_or_default(UserChatRelation, user_id=user.id, chat_id=chat_id)
    user_chat_relation.at_message_id = 0
    user_chat_relation.unread = 0
    user_chat_relation.save()
    data.update(_get_chat_members(chat_id, org_id, user.id))
    data.update(get_at_list(user, chat_id))
    # 返回所有未读at消息，然后把它们valid置零

    # 返回该群聊所有消息
    # 调用pull all
    return data


def get_at_list(user, chat_id):
    data = {"at_list": []}

    # # 获取最新未读at消息，并且置零，重新加载解锁查看静态的最新消息，unread置零
    # user_chat_relation = first_or_default(UserChatRelation, user_id=user.id, chat_id=chat_id)
    # at_message_id = user_chat_relation.at_message_id
    #
    # user_chat_relation.at_message_id = 0
    # user_chat_relation.unread = 0
    # user_chat_relation.save()

    # 返回所有未读at消息，然后把它们valid置零
    user_chat_jump_list = UserChatJump.objects.filter(user_id=user.id, chat_id=chat_id, valid=1)  # 顺序
    for user_chat_jump in user_chat_jump_list:
        at_message_id = user_chat_jump.message_id
        data["at_list"].append(at_message_id)
        user_chat_jump.valid = 0
        user_chat_jump.save()
    return data


def pull_all(chat_id, org_id):
    message_list = Message.objects.filter(chat_id=chat_id)
    # 获取群聊列表：基础信息
    return pull_message(message_list, org_id)


# 判断是否足够
def pull_newer(message_id, chat_id, message_num, org_id):
    if Message.objects.filter(chat_id=chat_id, id__gte=message_id).count() < message_num:
        message_list = Message.objects.filter(chat_id=chat_id, id__gte=message_id)
    else:
        message_list = Message.objects.filter(chat_id=chat_id, id__gte=message_id)[:message_num]
    # 获取群聊列表：基础信息

    return pull_message(message_list, org_id)


# 判断是否足够
def pull_older(message_id, chat_id, message_num, org_id):
    if Message.objects.filter(chat_id=chat_id, id__lte=message_id).count() < message_num:
        message_list = Message.objects.filter(chat_id=chat_id, id__lte=message_id)
    else:
        message_list = Message.objects.filter(chat_id=chat_id, id__lte=message_id)[:-message_num]

    # 获取群聊列表：基础信息
    return pull_message(message_list, org_id)


def pull_message(message_list, org_id):
    data = {"message_list": []}
    for message in message_list:
        user_organization_profile = first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                                     org_id=org_id)
        if user_organization_profile is not None:
            nickname = user_organization_profile.nickname
        else:
            nickname = ""
        tmp = {

            # "message_id": message.id,
            "_id": message.id,
            "index_id": message.id,
            "content": message.text,
            "is_record": message.is_record,
            "system": bool(message.is_system),
            "message_type": message.type,
            "senderId": str(message.src_id),
            "avatar": get_avatar_url("user", first_or_default(User, id=message.src_id).avatar),
            "username": nickname,
            "timestamp": get_time(message.timestamp),
            "date": get_date(message.timestamp),
            "saved": False,
            "distributed": False,
            "seen": False,
            "files": [],
        }
        if message.is_system == 1:
            tmp["username"] = ""
            tmp["senderId"] = ""
        if message.file is not None and message.file.name is not None and message.file.name != "" and message.is_record == 0:
            tmp["content"] = ""
            tmp["files"].append({
                "name": message.text,
                "size": 0,  # TODO: 预留
                "type": message.file.name.split('.')[-1],
                "audio": False,  # TODO: 预留
                "duration": 0,  # TODO: 预留
                "url": BASE_URL + message.file.url
            })
        if message.is_record == 1:
            son_list = [m2m.son for m2m in M2M.objects.filter(father=message.id)]
            tmp["content"] = ""
            tmp["files"].append({
                "name": "聊天记录",
                "size": 0,  # TODO: 预留
                "type": "docx",
                "audio": False,  # TODO: 预留
                "duration": 0,  # TODO: 预留
                "son_list": son_list,
                "url": ""
            })
        data["message_list"].append(tmp)
    return data


def _send_message(user_id, text, org_id, org, chat_id, chat, at_list, nickname, extension, file, sys):
    user = first_or_default(User, id=user_id)


    response = {
        "senderId": user.id,
        "username": nickname,  # 传过来团队内昵称
        "avatar": get_avatar_url("user", user.avatar),  # TODO: 可以前端存储
        "saved": False,
        "distributed": False,
        "seen": False,
        "system": bool(sys)
    }
    if sys == 1:
        response["username"] = ""
        response["senderId"] = ""
    message = Message(src_id=user.id, chat_id=chat_id)
    message.is_system = sys
    if text is not None and text != "":
        message.text = text
        response['content'] = text
        message.type = MessageType.TEXT
        message.save()
        if at_list is not None and len(at_list) != 0:
            for user_id in at_list:
                # 更新at消息列表，群聊最新消息
                user_chat_relation = first_or_default(UserChatRelation, chat_id=chat_id)
                user_chat_relation.at_message_id = message.id
                user_chat_relation.save()
                user_chat_jump = UserChatJump(user_id=user_id, chat_id=chat_id, message_id=message.id,
                                              valid=1)
                user_chat_jump.save()

                notif_at_payload = NotifAtPayload(org, user, chat)
                dispatch_notification(user_id, org_id, notif_at_payload)

                response["at_list"] = at_list
    if file is not None and file != "" and file.name != "":
        file.name = file.name + "." + extension
        message.file = file  # 组合方式
        message.text = file.name  # 本名
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tiff']
        video_extensions = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
        if extension in image_extensions:
            message.type = MessageType.IMAGE
        elif extension in video_extensions:
            message.type = MessageType.VIDEO
        else:
            message.type = MessageType.FILE
        message.save()
        response['content'] = ""
        response["files"] = []
        response['files'].append({
            "name": file.name,
            "size": 0,  # TODO: 预留
            "type": extension,
            "audio": False,  # TODO: 预留
            "duration": 0,  # TODO: 预留
            "url": BASE_URL + message.file.url,
            # preview
            # "progress": 100,  # TODO: 预留
        })

    response.update({
        "_id": message.id,
        "indexId": 0,  # TODO: 预留
        "timestamp": get_time(message.timestamp),
        "date": get_date(message.timestamp),
    })

    # 更新最新消息

    chat.latest_message = message.id
    chat.save()

    # 更新未读信息数目

    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user_chat_relation.unread += 1

        user_chat_relation.save()

    channel_layer = channel_layers[ChatMessageConsumer.channel_layer_alias]
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

            "saved": False,
            "distributed": False,
            "seen": False,
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
    return response
