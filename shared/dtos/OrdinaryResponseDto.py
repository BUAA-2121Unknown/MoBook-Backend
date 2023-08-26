# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:25
# @Author  : Tony Skywalker
# @File    : OrdinaryResponseDto.py
#
# Description:
#   Basic bad request dto template class.
#

from shared.dtos.BaseResponseDto import BaseResponseDto


class OkDto(BaseResponseDto):
    def __init__(self, msg="What a nice request!", **kwargs):
        super().__init__(0, msg, **kwargs)


class ErrorDto(BaseResponseDto):
    def __init__(self, code: object = -1, msg: object = "Not available", **kwargs: object) -> object:
        super().__init__(code, msg, **kwargs)


class BadRequestDto(BaseResponseDto):
    def __init__(self, msg="Bad request", **kwargs):
        super().__init__(400, msg, **kwargs)


class UnauthorizedDto(BaseResponseDto):
    def __init__(self, msg="Unauthorized", **kwargs):
        super().__init__(401, msg, **kwargs)


class ForbiddenDto(BaseResponseDto):
    def __init__(self, msg="Forbidden", **kwargs):
        super().__init__(403, msg, **kwargs)


class NotFoundDto(BaseResponseDto):
    def __init__(self, msg="Not Found", **kwargs):
        super().__init__(404, msg, **kwargs)


class InternalServerErrorDto(BaseResponseDto):
    def __init__(self, msg="Internal Server Error", **kwargs):
        super().__init__(500, msg, **kwargs)
