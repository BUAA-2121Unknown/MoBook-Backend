# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 16:46
# @Author  : Tony Skywalker
# @File    : dir_utils.py
#
import os

from MoBook.settings import BASE_URL
from artifact.models import Item

AVATAR_BASE_PATH = {
    "user": "./media/avatar/user",
    "org": "./media/avatar/org",
    "proj": "./media/avatar/proj",
}

AVATAR_BASE_URL = {
    "user": f"{BASE_URL}/media/avatar/user/",
    "org": f"{BASE_URL}/media/avatar/org/",
    "proj": f"{BASE_URL}/media/avatar/proj/",
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


def get_imagefield_url(filename):
    if filename is None:
        return None
    return BASE_URL + filename.url


def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def ensure_file_parent_path(path):
    ensure_path(os.path.dirname(path))


def get_item_path(item: Item, version: int):
    return f"./files/artifacts/{item.org_id}/{item.proj_id}/{item.id}/{version}{item.extension}"


def get_item_folder(item: Item):
    return f"./files/artifacts/{item.org_id}/{item.proj_id}/{item.id}/"
