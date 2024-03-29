# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 16:07
# @Author  : Tony Skywalker
# @File    : user_extension.py
#
# Description:
#   Provide a way to get user from request.
#
from django.core.handlers.wsgi import WSGIRequest

from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.token.exception import TokenException
from shared.utils.token.jwt_token import verify_jwt_token
from user.models import User


def _get_user_from_jwt(request: WSGIRequest):
    token = request.META.get('HTTP_AUTHORIZATION', None)
    if token is None:
        raise TokenException("Missing Authorization")
    try:
        data = verify_jwt_token(token)
    except TokenException as e:
        raise e
    key, user = first_or_default_by_cache(User, data)
    user: User
    if user is None or not user.activated:
        return None
    return user


def get_user_from_request(request: WSGIRequest, raise_exception=False):
    try:
        return _get_user_from_jwt(request)
    except TokenException as e:
        if raise_exception:
            raise e
        else:
            return None


def get_user_by_id(uid):
    _, user = first_or_default_by_cache(User, uid)
    return user
