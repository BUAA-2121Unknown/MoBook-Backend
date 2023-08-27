# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 17:02
# @Author  : Tony Skywalker
# @File    : avatar_util.py
#
import os

from shared.utils.dir_utils import ensure_avatar_path


def save_avatar(typ, old_path, new_path, file):
    ensure_avatar_path(typ)
    if old_path and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception:
            # shouldn't raise exception! swallow it!
            pass

    try:
        f = open(new_path, "wb")
        for chunk in file.chunks():
            f.write(chunk)
        f.close()
    except Exception as e:
        raise e
