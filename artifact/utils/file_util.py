# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 12:59
# @Author  : Tony Skywalker
# @File    : file_util.py
#
from artifact.models import Item, FileVersion
from shared.utils.dir_utils import get_item_path, ensure_file_parent_path
from shared.utils.file.file_handler import save_file
from user.models import User


def create_version_aux(file, version, item: Item, user: User):
    create_version_aux_by_user_id(file, version, item, user.id)


def create_version_aux_by_user_id(file, version, item: Item, user_id):
    if version > item.version:
        version = item.version + 1

    item.version = version
    item.save()

    # delete version on other branches
    FileVersion.objects.filter(file_id=item.id, version__gte=version).delete()

    # create new version
    version = FileVersion.create(version, item.id, user_id)
    version.save()

    # get internal file storage path
    path = get_item_path(item, version.version)

    if file is not None:
        # save actual file
        save_file(None, path, file)
    else:
        # save an empty file
        ensure_file_parent_path(path)
        fp = open(path, 'w')
        fp.close()

    return version
