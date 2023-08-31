# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 20:09
# @Author  : Tony Skywalker
# @File    : duplicate.py
#
from artifact.models import Item, FileVersion
from artifact.utils.file_util import create_version_aux_by_user_id
from project.models import Project
from shared.utils.dir_utils import get_item_path
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import load_file
from shared.utils.model.item_extension import get_item_lambda
from shared.utils.model.model_extension import first_or_default


def duplicate_files(src_proj: Project, dst_proj: Project):
    """
    duplicate files in a project. root folder should be initialized ahead
    """
    src_root: Item = first_or_default(Item, id=src_proj.root_id)
    dst_root: Item = first_or_default(Item, id=dst_proj.root_id)
    if src_root is None or dst_root is None:
        # failed...
        return

    for item in src_root.get_children():
        duplicate_item_aux(dst_root, item)


def duplicate_item_aux(parent: Item, template: Item):
    if template.is_dir():
        return _duplicate_folder(parent, template)
    else:
        return _duplicate_file(parent, template)


def _duplicate_folder(parent: Item, template: Item):
    """
    duplicate folder and its descendents under parent
    """
    if not template.is_dir():
        return None

    node = parent.add_child(name=template.name,
                            extension=template.extension,
                            type=template.type,
                            prop=template.prop,
                            proj_id=template.proj_id,
                            org_id=template.org_id)
    folder = get_item_lambda()(node.pk)
    for item in template.get_children():
        duplicate_item_aux(folder, item)

    return folder


def _duplicate_file(parent: Item, template: Item):
    """
    duplicate a single file under parent
    """
    if not template.is_file():
        return None

    node = parent.add_child(name=template.name,
                            extension=template.extension,
                            type=template.type,
                            prop=template.prop,
                            proj_id=template.proj_id,
                            org_id=template.org_id)
    file = get_item_lambda()(node.pk)
    template_version: FileVersion = first_or_default(FileVersion, file_id=template.id, version=template.version)
    if template_version is None:
        return None

    template_path = get_item_path(template, template.version)
    try:
        f = load_file(template_path)
        create_version_aux_by_user_id(f, 1, file, template_version.user_id)
    except FileException as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None

    return file
