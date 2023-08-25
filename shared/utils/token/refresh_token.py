# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 9:06
# @Author  : Tony Skywalker
# @File    : refresh_token.py
#
from datetime import timedelta
from random import Random

from django.utils import timezone

from oauth.models import RefreshToken
from shared.utils.token.exception import TokenException

CODE_CHARACTER_SET = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789~!@#$%^&*()-+=[]{}|:;<>,.?'


def _generate_code(length=6) -> str:
    code = ""
    max_idx = len(CODE_CHARACTER_SET) - 1
    random = Random()
    for i in range(length):
        code += CODE_CHARACTER_SET[random.randint(0, max_idx)]
    return code


def generate_refresh_token(uid):
    try:
        token = _generate_code(32)
        created = timezone.now()
        expires = created + timedelta(days=14)
        refresh_token = RefreshToken.create(uid, token, created, expires)
        return refresh_token
    except Exception as e:
        raise TokenException("Failed to generate refresh token") from e
