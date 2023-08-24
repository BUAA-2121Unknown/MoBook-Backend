# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 21:08
# @Author  : Tony Skywalker
# @File    : jwt_token.py
#
import base64
import secrets
from datetime import timedelta

from django.utils import timezone

from oauth.models import RefreshToken
from shared.utils.jwt_token.code_generator import generate_code
from shared.utils.jwt_token.jwt_token import generate_token


def generate_jwt_token(data):
    try:
        return generate_token(data)
    except Exception as e:
        print(e)
        raise e


# refresh token will expire after 14 days
def generate_refresh_token(uid):
    try:
        token = generate_code(32)
        created = timezone.now()
        expires = created + timedelta(days=14)
        refresh_token = RefreshToken.create(uid, token, created, expires)
        refresh_token.save()
        return refresh_token
    except Exception as e:
        print(e)
        raise e
