# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 19:40
# @Author  : Tony Skywalker
# @File    : user_dto.py
#
from shared.utils.dir_utils import get_avatar_url
from user.models import User


class UserDto:
    def __init__(self, user: User):
        self.id = None if user is None else user.id
        self.username = None if user is None else user.username
        self.name = None if user is None else user.name
        self.avatarUrl = None if user is None else get_avatar_url('user', user.avatar)
        self.email = None if user is None else user.email
