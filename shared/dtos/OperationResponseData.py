# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 19:55
# @Author  : Tony Skywalker
# @File    : OperationResponseData.py
#
from typing import List


class OperationErrorData:
    def __init__(self, _id: int = 0, _msg: str = ""):
        self.id: int = _id
        self.message: str = _msg


class OperationResponseData:
    def __init__(self):
        self.errors: List[OperationErrorData] = [OperationErrorData()]
        self.success: List[int] = [0]

    def init(self):
        self.errors.clear()
        self.success.clear()
        return self
