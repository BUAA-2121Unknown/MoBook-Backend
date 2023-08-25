# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:18
# @Author  : Tony Skywalker
# @File    : get_token_dto.py
#


class GetTokenDto:
    def __init__(self):
        self.id: int = 0
        self.password: str = ""


class GetTokenSuccessDto:
    def __init__(self, uid, token, refresh_token_expiration):
        self.id = uid
        self.token = token
        self.refreshTokenExpiration = refresh_token_expiration
