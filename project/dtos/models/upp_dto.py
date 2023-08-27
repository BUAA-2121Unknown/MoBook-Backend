# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 22:33
# @Author  : Tony Skywalker
# @File    : upp_dto.py
#
from user.dtos.user_dto import UserDto
from user.models import UserProjectProfile, User


class UppData:
    def __init__(self, upp: UserProjectProfile):
        self.projId = upp.proj_id
        self.role = upp.role


class UppDto:
    def __init__(self, user: User, upp: UserProjectProfile):
        self.user = UserDto(user)
        self.member = UppData(upp)
