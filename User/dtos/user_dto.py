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
        self.id = user.id
        self.username = user.username
        self.name = user.name
        self.avatarUrl = get_avatar_url('user', user.avatar)
