# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 22:07
# @Author  : Tony Skywalker
# @File    : delete.py
#
import shutil

from artifact.models import Item, FileVersion
from shared.utils.dir_utils import get_item_folder


def delete_item_aux(item: Item):
    if item.is_dir():
        _delete_folder(item)
    else:
        _delete_file(item)


def _delete_folder(folder: Item):
    for item in folder.get_descendants():
        delete_item_aux(item)
    folder.delete()


def _delete_file(file: Item):
    FileVersion.objects.filter(file_id=file.id).delete()
    path = get_item_folder(file)
    shutil.rmtree(path, ignore_errors=True)
    file.delete()
