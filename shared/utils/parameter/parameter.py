# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/23/2023 21:40
# @Author  : Tony Skywalker
# @File    : parameter.py
#
# Description:
#   Parameter adapter, convert request parameters into a dictionary.
#

from django.core.handlers.wsgi import WSGIRequest

from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.parameter.exceptions import ParameterException


def _parse_post_param(request: WSGIRequest, raise_exception=False) -> dict:
    content_type: str = str(request.headers.get("Content-Type"))
    if content_type == "application/json":
        try:
            return deserialize(request.body)
        except JsonDeserializeException as e:
            if raise_exception:
                raise ParameterException("Bad parameter format") from e
            else:
                return {}
    elif content_type == "application/x-www-form-urlencoded":
        return request.POST.dict()
    elif content_type.startswith("multipart/form-data"):
        return request.POST.dict()
    if raise_exception:
        raise ParameterException("Unexpected POST content type: " + content_type)
    return {}


def _parse_get_param(request: WSGIRequest, raise_exception=False) -> dict:
    return request.GET.dict()


def parse_param(request: WSGIRequest, raise_exception=False) -> dict:
    """
    This will not handle multipart/form-data request!
    :return: all parameters in dictionary
    """
    if request.method == "POST":
        return _parse_post_param(request)
    elif request.method == "GET":
        return _parse_get_param(request)
    if raise_exception:
        raise ParameterException("Unsupported request method")
    return {}
