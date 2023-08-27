# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 0:09
# @Author  : Tony Skywalker
# @File    : chat_extension.py
#
from chat.models import Chat
from org.models import Organization
from shared.utils.model.model_extension import first_or_default
from user.models import User, UserChatRelation


def get_chat_relation(user: User, chat: Chat):
    return first_or_default(UserChatRelation, user_id=user.id, chat_id=chat.id)


def get_chats_of_organization(organization: Organization):
    return Chat.objects.filter(org_id=organization.id)
