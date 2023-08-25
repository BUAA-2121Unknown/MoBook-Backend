# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:13
# @Author  : Tony Skywalker
# @File    : validator.py
#
import re


def validate_username(username: str) -> bool:
    if re.match('^[a-zA-Z_-]{4,16}$', username):
        return True
    return False


def validate_email(email: str) -> bool:
    if re.match('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
        return True
    return False


def validate_password(password: str) -> bool:
    if re.match('^[a-zA-Z0-9_]{6,16}$', password):
        return True
    return False
