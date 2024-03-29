# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 12:59
# @Author  : Tony Skywalker
# @File    : file_util.py
#
from artifact.models import Item, FileVersion
from shared.utils.dir_utils import get_item_path, ensure_file_parent_path
from shared.utils.file.file_handler import save_file
from shared.utils.model.model_extension import first_or_default
from user.models import User

# EMPTY_DOC_CONTENT = '{"type":"doc","content":[{"type":"title","attrs":{"level":1}}]}'
EMPTY_DOC_CONTENT = '{"default":{"type":"doc","content":[{"type":"title","attrs":{"level":1}},{"type":"title","attrs":{"level":1}}]}}'
EMPTY_PROTO_CONTENT = '{"canvasData":{"array":[]},"canvasStyle":{"width":1200,"height":740,"scale":100,"color":"#000","opacity":1,"background":"#fff","fontSize":14}}'


def _get_or_create_file_version(item_id, version, user_id):
    ver = first_or_default(FileVersion, file_id=item_id, version=version)
    if ver is None:
        ver = FileVersion.create(version, item_id, user_id)
        ver.save()
    return ver


def create_version_aux(file, version, item: Item, user: User):
    create_version_aux_by_user_id(file, version, item, user.id)


def create_version_by_content_aux(content, version, item: Item, user: User):
    create_version_by_content_aux_by_user_id(content, version, item, user.id)


def create_version_aux_by_user_id(file, version, item: Item, user_id):
    if version > item.total_version:
        version = item.total_version + 1

    item.version = version
    item.save()

    # delete version on other branches
    # FileVersion.objects.filter(file_id=item.id, version__gte=version).delete()

    # create new version
    file_version = _get_or_create_file_version(item.id, version, user_id)

    # get internal file storage path
    path = get_item_path(item, file_version.version)

    if file is not None:
        # save actual file
        save_file(None, path, file)
    else:
        # save an empty file
        ensure_file_parent_path(path)
        fp = open(path, 'wb')
        fp.close()

    return file_version


def create_version_by_content_aux_by_user_id(content, version, item: Item, user_id):
    if version > item.total_version:
        version = item.total_version + 1
        item.total_version = version
        item.version = item.total_version
    elif version <= 0:
        version = item.version
    else:
        item.version = version
    item.save()

    # delete version on other branches
    # FileVersion.objects.filter(file_id=item.id, version__gte=version).delete()

    # create new version
    file_version = _get_or_create_file_version(item.id, version, user_id)

    # get internal file storage path
    path = get_item_path(item, file_version.version)
    ensure_file_parent_path(path)

    content = refine_content(item, content)

    with open(path, 'w') as f:
        f.write(content)

    return file_version


def refine_content(item: Item, content):
    if content is None or len(content) == 0:
        if item.is_doc():
            return EMPTY_DOC_CONTENT
        elif item.is_prototype():
            return EMPTY_PROTO_CONTENT
        else:
            return ""
    return content
