# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 0:50
# @Author  : Tony Skywalker
# @File    : assistance.py
#
from chat.models import Chat, ChatType
from org.models import Organization
from shared.dtos.OperationResponseData import OperationResponseData
from shared.utils.model.chat_extension import get_chat_relation
from shared.utils.model.model_extension import first_or_default
from user.models import User, UserChatRelation, ChatAuth


def add_users_to_chat_by_id(users, chat: Chat):
    data = OperationResponseData().init()
    user_list = []
    for uid in users:
        user = first_or_default(User, id=uid)
        if user is None:
            data.add_error(uid, "No such user")
            continue
        user_list.append(user)
    _add_users_to_chat(user_list, chat, data)
    return data


def add_users_to_chat(users, chat: Chat):
    data = OperationResponseData().init()
    _add_users_to_chat(users, chat, data)
    return data


def _add_users_to_chat(users, chat: Chat, data: OperationResponseData):
    for user in users:
        ucr = get_chat_relation(user, chat)
        if ucr is not None:
            data.add_error(user.id, "User already in chat")
            continue
        UserChatRelation.create(user.id, chat.id, chat.org_id, ChatAuth.NORMAL).save()
        data.add_success(user.id)


def remove_users_from_chat_by_id(users, chat: Chat):
    data = OperationResponseData().init()
    user_list = []
    for uid in users:
        user = first_or_default(User, id=uid)
        if user is None:
            data.add_error(uid, "No such user")
            continue
        user_list.append(user)
    _remove_users_from_chat(user_list, chat, data)
    return data


def remove_users_from_chat(users, chat: Chat):
    data = OperationResponseData().init()
    _remove_users_from_chat(users, chat, data)
    return data


def _remove_users_from_chat(users, chat: Chat, data: OperationResponseData):
    if chat.type == ChatType.PUBLIC:
        for user in users:
            ucr: UserChatRelation = get_chat_relation(user, chat)
            if ucr is None:
                data.add_error(user.id, "User not in chat")
                continue
            ucr.delete()
            data.add_success(user.id)
    else:
        # delete chat
        UserChatRelation.objects.filter(chat_id=chat.id)
        chat.delete()
        data.add_success(chat.id)


def init_default_chat(org: Organization, user: User):
    chat = Chat.create(org.id, org.name, ChatType.PUBLIC)
    chat.save()

    UserChatRelation.create(user.id, chat.id, org.id, ChatAuth.ADMIN).save()

    return chat
