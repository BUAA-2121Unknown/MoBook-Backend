# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/29/2023 17:02
# @Author  : Tony Skywalker
# @File    : item_util.py
#
# Description:
#   Artifact creation utils.
#
from typing import List

from artifact.models import Item, ItemType, ItemProperty
from artifact.utils.file_util import create_version_aux, create_version_by_content_aux
from project.models import Project
from shared.utils.cache.cache_utils import update_cached_object
from shared.utils.file.file_handler import parse_filename
from shared.utils.model.item_extension import get_item_lambda
from user.models import User


def init_root_folder(proj: Project, user: User):
    """
    Initialize root folder for the given project.
    """
    node = Item.add_root(name=proj.name,
                         type=ItemType.ROOT,
                         prop=ItemProperty.FOLDER,
                         proj_id=proj.id,
                         org_id=proj.org_id,
                         user_id=user.id)
    root = get_item_lambda()(node.pk)

    proj.root_id = root.pk
    proj.save()
    update_cached_object(Project, proj.id, proj)


def create_folder_aux(dst: Item, name: str, proj: Project, user: User):
    """
    Create a folder under dst item.
    """
    node = dst.add_child(name=name,
                         extension="",
                         type=ItemType.DIRECTORY,
                         prop=ItemProperty.FOLDER,
                         proj_id=proj.id,
                         org_id=proj.org_id,
                         user_id=user.id)
    return get_item_lambda()(node.pk)


def create_file_aux(dst: Item, filename: str, prop: int, live: bool, file, user: User, proj: Project):
    """
    Create a file under dst item.
    """

    name, ext = parse_filename(filename)

    # if ext == "":
    #     raise FileException("Missing extension")

    # first, create a file item
    node = dst.add_child(name=name,
                         extension=ext,
                         type=ItemType.FILE,
                         prop=prop,
                         live=live,
                         proj_id=proj.id,
                         org_id=proj.org_id,
                         user_id=user.id)
    item = get_item_lambda()(node.pk)

    # then create a version
    version = create_version_aux(file, 1, item, user)

    return item, version


def create_file_by_content_aux(dst: Item, filename: str, prop: int, live: bool, content: str, user: User,
                               proj: Project):
    """
    Create a file under dst item.
    """

    name, ext = parse_filename(filename)

    # if ext == "":
    #     raise FileException("Missing extension")

    # first, create a file item
    node = dst.add_child(name=name,
                         extension=ext,
                         type=ItemType.FILE,
                         prop=prop,
                         live=live,
                         proj_id=proj.id,
                         org_id=proj.org_id,
                         user_id=user.id)
    item = get_item_lambda()(node.pk)

    # then create a version
    version = create_version_by_content_aux(content, 1, item, user)

    return item, version


def move_item_aux(src: Item, dst: Item):
    """
    Move src item as child of dst item.
    """
    if dst.type not in ItemType.dirs():
        return
    src.move(dst, 'sorted-child')


def update_item_status_aux(item: Item, status: int):
    """
    update given item's status.
    """
    if item.type == ItemType.ROOT:
        # root status should not be changed
        item.get_descendants().update(status=status)
    elif item.prop == ItemProperty.FOLDER:
        item.get_descendants().update(status=status)
        item.status = status
        item.save()
    else:
        item.status = status
        item.save()


def update_items_status_aux(items: List[Item], status: int):
    for item in items:
        update_item_status_aux(item, status)
