# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 16:46
# @Author  : Tony Skywalker
# @File    : dir_utils.py
#
import os

BASE_URL = "http://81.70.161.76:5000/"
AVATAR_BASE_PATH = {
    "user": "./media/avatar/user",
    "org": "./media/avatar/org"
}

AVATAR_BASE_URL = {
    "user": f"{BASE_URL}media/avatar/user/",
    "org": f"{BASE_URL}media/avatar/org/"
}


def ensure_avatar_path(typ):
    path = AVATAR_BASE_PATH.get(typ, None)
    if path is not None and not os.path.exists(path):
        os.makedirs(path)


def get_avatar_path(typ, filename):
    if filename is None:
        return None

    path = AVATAR_BASE_PATH.get(typ, None)
    if path is None:
        return
    return os.path.join(path, filename)


def get_avatar_url(typ, filename):
    if filename is None:
        return None

    url = AVATAR_BASE_URL.get(typ, None)
    if url is None:
        return None
    return url + filename
