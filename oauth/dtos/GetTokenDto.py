# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:18
# @Author  : Tony Skywalker
# @File    : get_token_dto.py
#
from datetime import datetime


class GetTokenDto:
    def __int__(self):
        self.id: int = 0
        self.password: str = ""


class GetTokenSuccessDto:
    def __init__(self, id, token, refresh_token_expiration: datetime):
        self.id = id
        self.token = token
        self.refreshTokenExpiration = refresh_token_expiration.strftime()
