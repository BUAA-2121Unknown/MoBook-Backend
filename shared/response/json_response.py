# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/23/2023 22:21
# @Author  : Tony Skywalker
# @File    : json_response.py
#
from http import HTTPStatus

from django.http import HttpResponse

from shared.utils.json.serializer import serialize


class BaseResponse(HttpResponse):
    def __init__(self, dto, status=HTTPStatus.OK):
        super().__init__(
                serialize(dto),
                status=status,
                content_type="application/json",
                charset="utf-8",
        )


class OkResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.OK)


class BadRequestResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.BAD_REQUEST)


class UnauthorizedResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.UNAUTHORIZED)


class ForbiddenResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.FORBIDDEN)


class InternalServerErrorResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.INTERNAL_SERVER_ERROR)


class NotFoundResponse(BaseResponse):
    def __init__(self, dto):
        super().__init__(dto, HTTPStatus.NOT_FOUND)
