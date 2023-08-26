# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 19:48
# @Author  : Tony Skywalker
# @File    : paged_request_dto.py
#

class PagedRequestDto:
    def __init__(self):
        self.ps: int = 0
        self.p: int = 0

    def is_valid(self):
        return self.ps > 0 and self.p > 0
