# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/29/2023 17:02
# @Author  : Tony Skywalker
# @File    : artifact.py
#
# Description:
#   Artifact creation utils.
#
from typing import List

from artifact.models import Item, ItemType, ItemProperty
from project.models import Project
from shared.utils.model.item_extension import get_item_lambda
from user.models import User


def init_root_folder(proj: Project):
    """
    Initialize root folder for the given project.
    """
    node = Item.add_root(name=proj.name,
                         type=ItemType.ROOT,
                         property=ItemProperty.FOLDER,
                         proj_id=proj.id,
                         org_id=proj.org_id)
    root = get_item_lambda()(node.pk)

    proj.root_id = root.pk
    proj.save()


def create_folder_aux(dst: Item, name: str, proj: Project):
    """
    Create a folder under dst item.
    """
    node = dst.add_child(name=name,
                         type=ItemType.DIRECTORY,
                         property=ItemProperty.FOLDER,
                         proj_id=proj.id,
                         org_id=proj.org_id)
    return get_item_lambda()(node.pk)


def create_file_aux(dst: Item, name: str, prop: int, live: bool, user: User, proj: Project):
    """
    Create a file under dst item.
    """

    # first, create a file
    node = dst.add_child(name=name,
                         type=ItemType.FILE,
                         property=prop,
                         proj_id=proj.id,
                         org_id=proj.org_id)
    file = get_item_lambda()(node.pk)

    # then create a file item

    pass


def move_item_aux(src: Item, dst: Item):
    """
    Move src item as child of dst item.
    """


def update_item_status_asx(items: List[Item], status: int):
    """
    update given items' status.
    """
