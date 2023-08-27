# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 10:58
# @Author  : Tony Skywalker
# @File    : file_handler.py
#

import os

from shared.utils.file.exceptions import FileException


def save_file(old_path, new_path, file):
    if old_path and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            raise FileException("Failed to remove old file") from e

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

# response = FileResponse(open(md_url, "rb"))
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(document.document_title + '.md'))
# return response
