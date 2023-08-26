# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 10:22
# @Author  : Tony Skywalker
# @File    : token.py
#
from random import Random

BASIC_TOKEN_CHARS = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
SPECIAL_TOKEN_CHARS = '~!@#$%^&*()-+=[]{}|:;<>,.?'


def generate_basic_token(length=6, include_special=False) -> str:
    chars = ""
    chars += BASIC_TOKEN_CHARS
    if include_special:
        chars += SPECIAL_TOKEN_CHARS

    token = ""
    max_idx = len(chars) - 1
    random = Random()
    for i in range(length):
        token += chars[random.randint(0, max_idx)]

    return token
