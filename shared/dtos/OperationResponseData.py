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

    def add_error(self, _id: int, _msg: str = ""):
        self.errors.append(OperationErrorData(_id=_id, _msg=_msg))
        return self

    def add_success(self, _id: int):
        self.success.append(_id)
        return self
