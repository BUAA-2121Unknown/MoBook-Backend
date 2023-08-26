# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:45
# @Author  : Tony Skywalker
# @File    : login_dto.py
from user.utils.user_profile_provider import user_profile_provider_full


class LoginDto:
    def __init__(self):
        self.username: str = ""
        self.password: str = ""


class LoginSuccessDto:
    def __init__(self, user, token):
        self.user = user_profile_provider_full(user)
        self.token = token
