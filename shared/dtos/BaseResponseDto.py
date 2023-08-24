# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:25
# @Author  : Tony Skywalker
# @File    : BaseResponseDto.py
#
# Description:
#   Base class of all response dtos.
#

class BaseResponseDto:
    # Only accept 'data' as kwargs
    def __init__(self, code, msg="Not available", **kwargs):
        self.meta = {'status': code, 'msg': msg}
        self.data = kwargs.get('data', {})
