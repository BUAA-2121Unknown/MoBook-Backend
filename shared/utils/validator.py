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


def validate_name(name: str) -> bool:
    if re.match('^([\u4e00-\u9fa5]{2,8}|[a-zA-Z.\\s]{2,20})$', name):
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


VALID_IMAGE_FILE_EXT = ['.jpg', '.jpeg', '.png']


def validate_image_name(filename: str) -> bool:
    for ext in VALID_IMAGE_FILE_EXT:
        if filename.endswith(ext):
            return True
    return False
