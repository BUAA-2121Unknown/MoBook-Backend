# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 16:47
# @Author  : Tony Skywalker
# @File    : chat_dto.py
#
from chat.models import Chat
from shared.utils.dir_utils import get_imagefield_url


class ChatDto:
    def __init__(self, chat: Chat):
        self.id = chat.id
        self.name = chat.chat_name
        self.avatar = get_imagefield_url(chat.chat_avatar)
        self.type = chat.type
