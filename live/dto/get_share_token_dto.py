# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 3:11
# @Author  : Tony Skywalker
# @File    : get_share_token_dto.py
#
from live.models import ShareAuth


class GetShareTokenDto:
    def __init__(self):
        self.itemId: int = 0
        self.expires: int = 0
        self.auth: int = 0
        self.orgOnly: bool = False

    def is_valid(self) -> bool:
        return self.auth in ShareAuth.valid()
