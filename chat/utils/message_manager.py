from MoBook.settings import BASE_URL
from chat.utils.chat_manager import _get_chat_members
from message.models import Message, M2M
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
    data.update(_get_chat_members(chat_id, org_id))
    # 返回所有未读at消息，然后把它们valid置零

    # 返回该群聊所有消息
    # 调用pull all
    return data


def get_at_list(user, chat_id):
    data = {"at_message_list": []}

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
        at_message_id = user_chat_jump.at_message_id
        data["at_message_list"].append(at_message_id)
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
        print("hello")
        print(message.is_record)
        tmp = {
            # "message_id": message.id,
            "_id": message.id,
            "index_id": message.id,
            "content": message.text,
            "is_record": message.is_record,
            "senderId": str(message.src_id),
            "avatar": get_avatar_url("user", first_or_default(User, id=message.src_id).avatar),
            "username": first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                         org_id=org_id).nickname,
            "timestamp": get_time(message.timestamp),
            "date": get_date(message.timestamp),
            "saved": True,
            "distributed": True,
            "seen": True,
            "files": []
        }
        if message.file is not None and message.file.name is not None and message.file.name != "":
            tmp["files"].append({
                "name": message.file.name,
                "size": 0,  # TODO: 预留
                "type": message.file.name.split('.')[-1],
                "audio": False,  # TODO: 预留
                "duration": 0,  # TODO: 预留
                "url": BASE_URL + message.file.url
            })
        if message.is_record == 1:
            son_list = [m2m.son for m2m in M2M.objects.filter(father=message.id)]
            tmp["son_list"] = son_list
        data["message_list"].append(tmp)
    return data
