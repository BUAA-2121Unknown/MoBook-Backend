# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 10:58
# @Author  : Tony Skywalker
# @File    : file_handler.py
#

import os

from django.http import FileResponse

from shared.utils.file.exceptions import FileException


def save_file(old_path, new_path, file):
    if old_path is not None and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            pass
            # raise FileException("Failed to remove old file") from e

    parent = os.path.dirname(new_path)
    if not os.path.exists(parent):
        os.makedirs(parent)

    try:
        f = open(new_path, "wb")
        for chunk in file.chunks():
            f.write(chunk)
        f.close()
    except Exception as e:
        raise FileException("Failed to write file") from e


def load_file(file_path):
    if not os.path.exists(file_path):
        raise FileException("File does not exist")
    try:
        return open(file_path, "rb")
    except Exception as e:
        raise FileException("Failed to open file") from e


def save_file_by_content(old_path, new_path, content):
    if old_path is not None and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            pass
            # raise FileException("Failed to remove old file") from e

    parent = os.path.dirname(new_path)
    if not os.path.exists(parent):
        os.makedirs(parent)

    try:
        with open(new_path, "w") as f:
            f.write(content)
    except Exception as e:
        raise FileException("Failed to write file") from e


def load_file_by_content(file_path):
    if not os.path.exists(file_path):
        raise FileException("File does not exist")
    try:
        content = ""
        with open(file_path, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        raise FileException("Failed to open file") from e


def parse_filename(filename: str) -> (str, str):
    name, ext = os.path.splitext(filename)
    return name, ext


def construct_file_response(file, filename):
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response
