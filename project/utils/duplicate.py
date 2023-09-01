# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 20:04
# @Author  : Tony Skywalker
# @File    : duplicate.py
#
from artifact.utils.item_util import init_root_folder
from project.models import Project


def duplicate_project(project: Project):
    # create a new project
    proj = Project.create(project.org_id, project.name + " (Copy)", project.description)
    proj.save()

    init_root_folder(proj)

    return proj
