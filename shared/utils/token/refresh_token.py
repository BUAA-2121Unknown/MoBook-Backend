# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 9:06
# @Author  : Tony Skywalker
# @File    : refresh_token.py
#
from datetime import timedelta

from django.utils import timezone

from oauth.models import RefreshToken
from shared.utils.token.exception import TokenException
from shared.utils.token.token import generate_basic_token


def generate_refresh_token(uid):
    try:
        token = generate_basic_token(32)
        created = timezone.now()
        expires = created + timedelta(days=14)
        refresh_token = RefreshToken.create(uid, token, created, expires)
        return refresh_token
    except Exception as e:
        raise TokenException("Failed to generate refresh token") from e
