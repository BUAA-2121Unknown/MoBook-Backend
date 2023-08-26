# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 12:33
# @Author  : Tony Skywalker
# @File    : kick_member_dto.py
#
from typing import List


class KickMemberDto:
    def __init__(self):
        self.orgId: int = 0
        self.members: List[int] = [0]


class KickMemberErrorData:
    def __init__(self, uid=0, message=""):
        self.id: int = uid
        self.message: str = message


class KickMemberSuccessData:
    def __init__(self):
        self.errors: List[KickMemberErrorData] = [KickMemberErrorData()]
        self.success: List[int] = [0]

    def init(self):
        self.errors.clear()
        self.success.clear()
