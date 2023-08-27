# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 23:15
# @Author  : Tony Skywalker
# @File    : project_extension.py
#
from project.models import Project
from shared.utils.model.model_extension import first_or_default
from user.models import User, UserProjectProfile


def get_proj_profile_of_user(proj: Project, user: User):
    # User Organization Profile
    return first_or_default(UserProjectProfile, proj_id=proj.id, user_id=user.id)


def _get_proj_and_profile_of_user(pid, user: User):
    if pid is None or user is None:
        return None, None

    proj = first_or_default(Project, id=pid)
    if proj is None:
        return None, None
    upp = get_proj_profile_of_user(proj, user)
    if upp is None:
        return None, None
    return proj, upp


def get_proj_with_user(pid, user: User):
    proj, upp = _get_proj_and_profile_of_user(pid, user)
    return proj, upp
