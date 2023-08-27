from message.models import Message
from user.models import UserChatRelation, UserChatJump


def new_to_chat(user, chat_id, message_num):
    data = {"message_list": [],
            "at_message_list": []}

    # 返回所有未读at消息，然后把它们valid置零
    data["at_message_list"].append(get_at_list(user, chat_id))

    # 返回该群聊所有消息
    # 调用pull older
    data["message_list"].append(pull_older(Message.objects.filter(chat_id=chat_id)[-1].id, chat_id, message_num))
    return data


def new_to_chat_ver1(user, chat_id):
    data = {"message_list": [],
            "at_message_list": []}

    # 返回所有未读at消息，然后把它们valid置零
    data["at_message_list"].append(get_at_list(user, chat_id))

    # 返回该群聊所有消息
    # 调用pull all
    data["message_list"].append(pull_all(chat_id))
    return data


def get_at_list(user, chat_id):
    data = {}

    # 获取最新未读at消息，并且置零，重新加载解锁查看静态的最新消息，unread置零
    user_chat_relation = UserChatRelation.objects.get(user_id=user.id, chat_id=chat_id)
    at_message_id = user_chat_relation.at_message_id
    user_chat_relation.at_message_id = 0
    user_chat_relation.unread = 0
    user_chat_relation.save()

    # 返回所有未读at消息，然后把它们valid置零
    user_chat_jump_list = UserChatJump.objects.filter(user_id=user.id, chat_id=chat_id, valid=1)  # 顺序
    for user_chat_jump in user_chat_jump_list:
        at_message_id = user_chat_jump.at_message_id
        data["at_message_list"].append(at_message_id)
        user_chat_jump.valid = 0
        user_chat_jump.save()
    return data


def pull_all(chat_id):
    data = {}
    message_list = Message.objects.filter(chat_id=chat_id)
    # 获取群聊列表：基础信息
    for message in message_list:
        data["message_list"].append({
            "message_id": message.c_id,
            "text": message.text,
            "type": message.type,
            "src_id": message.src_id,
            "timestamp": message.timestamp,
        })

        # 图片或者文件url
        if message.type == 1:
            data["message_list"].append({"image": message.image})
        elif message.type == 2:
            data["message_list"].append({"file": message.file})

    return data


# 判断是否足够
def pull_newer(message_id, chat_id, message_num):
    data = {}
    if Message.objects.filter(chat_id=chat_id, id__gt=message_id).count() < message_num:
        message_list = Message.objects.filter(chat_id=chat_id, id__gt=message_id)
    else:
        message_list = Message.objects.filter(chat_id=chat_id, id__gt=message_id)[:message_num]
    # 获取群聊列表：基础信息
    for message in message_list:
        data["message_list"].append({
            "message_id": message.c_id,
            "text": message.text,
            "type": message.type,
            "src_id": message.src_id,
            "timestamp": message.timestamp,
        })

        # 图片或者文件url
        if message.type == 1:
            data["message_list"].append({"image": message.image})
        elif message.type == 2:
            data["message_list"].append({"file": message.file})

    return data


# 判断是否足够
def pull_older(message_id, chat_id, message_num):
    data = {}
    if Message.objects.filter(chat_id=chat_id, id__lt=message_id).count() < message_num:
        message_list = Message.objects.filter(chat_id=chat_id, id__lt=message_id)
    else:
        message_list = Message.objects.filter(chat_id=chat_id, id__lt=message_id)[:-message_num]
    # 获取群聊列表：基础信息
    for message in message_list:
        data["message_list"].append({
            "message_id": message.c_id,
            "text": message.text,
            "type": message.type,
            "src_id": message.src_id,
            "timestamp": message.timestamp,
        })

        # 图片或者文件url
        if message.type == 1:
            data["message_list"].append({"image": message.image})
        elif message.type == 2:
            data["message_list"].append({"file": message.file})

    return data
