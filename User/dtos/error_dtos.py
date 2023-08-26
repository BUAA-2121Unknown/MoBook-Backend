# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 18:14
# @Author  : Tony Skywalker
# @File    : error_dtos.py
#
from shared.dtos.OrdinaryResponseDto import ErrorDto, NotFoundDto


class UserAlreadyRegisteredDto(ErrorDto):
    def __init__(self):
        super().__init__(100021, "User already registered")


class UsernameOccupiedDto(ErrorDto):
    def __init__(self):
        super().__init__(100022, "Username occupied")


class NoSuchUserDto(NotFoundDto):
    def __init__(self):
        super().__init__("No such user")
