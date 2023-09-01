# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 19:34
# @Author  : Tony Skywalker
# @File    : user_profile_provider.py
#
# Description:
#   Get user profile info in different details.
#
# Note:
#   For now, these two are the same. :(
#

from user.dtos.user_dto import UserDto
from user.models import User


def user_profile_provider_full(user: User):
    return UserDto(user)


def user_profile_provider_simple(user: User):
    return UserDto(user)
