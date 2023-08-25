# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 18:14
# @Author  : Tony Skywalker
# @File    : error_dtos.py
#
from shared.dtos.OrdinaryResponseDto import ErrorDto


class UserAlreadyRegisteredDto(ErrorDto):
    def __init__(self):
        super().__init__(100021, "User already registered")


class UsernameOccupiedDto(ErrorDto):
    def __init__(self):
        super().__init__(100022, "Username occupied")


class UserNotExistsDto(ErrorDto):
    def __init__(self):
        super().__init__(100023, "User not exists")
