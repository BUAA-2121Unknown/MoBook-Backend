# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 21:26
# @Author  : Tony Skywalker
# @File    : cancel_org_dto.py
#
from typing import List


class CancelOrgDto:
    def __init__(self):
        self.organizations: List[int] = [0]


class CancelOrgErrorData:
    def __init__(self, oid: int = 0, msg: str = ""):
        self.id: int = oid
        self.message: str = msg


class CancelOrgSuccessData:
    def __init__(self):
        self.errors: List[CancelOrgErrorData] = [CancelOrgErrorData()]
        self.success: List[int] = [0]

    def init(self):
        self.errors.clear()
        self.success.clear()
