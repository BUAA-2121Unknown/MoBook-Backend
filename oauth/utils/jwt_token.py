# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 21:08
# @Author  : Tony Skywalker
# @File    : jwt_token.py
#
import base64
import secrets
from datetime import datetime, timedelta

import jwt
from rest_framework_jwt.serializers import jwt_payload_handler

from MoBook import settings
from auth.models import RefreshToken


def generate_jwt_token(info):
    try:
        payload = jwt_payload_handler(info)
        token = jwt.encode(payload, settings.SECRET_KEY)
    except Exception as e:
        raise e


# refresh token will expire after 14 days
def generate_refresh_token(uid):
    random_bytes = secrets.token_bytes(32)
    token = base64.decodebytes(random_bytes)
    created = datetime.now()
    expires = created + timedelta(days=14)
    refresh_token = RefreshToken.create(uid, token, created, expires)
    refresh_token.save()

    return refresh_token
