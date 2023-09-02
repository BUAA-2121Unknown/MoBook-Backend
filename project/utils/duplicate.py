# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 20:04
# @Author  : Tony Skywalker
# @File    : duplicate.py
#
from artifact.models import Item
from artifact.utils.duplicate import duplicate_item_aux
from project.models import Project
from shared.utils.model.model_extension import first_or_default


def duplicate_project_aux(project: Project):
    # create a new project
    proj = Project.create(project.org_id, project.name + " (Copy)", project.description)
    proj.save()

    root = first_or_default(Item, id=project.root_id)
    if root is None:
        return proj

    new_root = duplicate_item_aux(None, root, proj.id)
    new_root.name = new_root.name + " (Copy)"
    new_root.save()
    proj.root_id = new_root.id
    proj.save()

    return proj
