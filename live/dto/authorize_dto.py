# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 9:02
# @Author  : Tony Skywalker
# @File    : authorize_dto.py
#

class AuthorizeDto:
    def __init__(self, auth: int, msg: str):
        self.auth = auth
        self.message = msg
