# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:24
# @Author  : Tony Skywalker
# @File    : password.py
#
from django.contrib.auth.hashers import make_password, check_password

from MoBook import settings

SALT = settings.SECRETS['signing']['salt']


def generate_password(password) -> str:
    return make_password(password, SALT, 'pbkdf2_sha1')


def verify_password(password, token) -> bool:
    return check_password(password, token)
