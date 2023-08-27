# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 14:10
# @Author  : Tony Skywalker
# @File    : assistance.py
#
# Description:
#   This will help add and remove members of a project
#
from org.models import Organization
from project.models import Project
from shared.dtos.OperationResponseData import OperationResponseData
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_users_of_org
from shared.utils.model.project_extension import get_proj_profile_of_user
from user.models import User, UserProjectProfile


def add_users_to_project_by_id(users, project: Project, callback=None):
    data = OperationResponseData().init()
    user_list = []
    for uid in users:
        user = first_or_default(User, id=uid)
        if user is None:
            data.add_error(uid, "No such user")
            continue
        user_list.append(user)
    _add_users_to_project(user_list, project, callback, data)
    return data


def add_users_to_project(users, project: Project, callback=None):
    data = OperationResponseData().init()
    _add_users_to_project(users, project, callback, data)
    return data


def _add_users_to_project(users, project: Project, callback, data: OperationResponseData):
    for user in users:
        upp = get_proj_profile_of_user(project, user)
        if upp is not None:
            data.add_error(user.id, "User already in project")
            continue
        UserProjectProfile.create(user, project, "Member").save()
        data.add_success(user.id)
        if callback:
            callback(user, project)


def remove_users_from_project_by_id(users, project: Project, callback=None):
    data = OperationResponseData().init()
    user_list = []
    for uid in users:
        user = first_or_default(User, id=uid)
        if user is None:
            data.add_error(uid, "No such user")
            continue
        user_list.append(user)
    _remove_users_from_project(user_list, project, callback, data)
    return data


def remove_users_from_project(users, project: Project, callback=None):
    data = OperationResponseData().init()
    _remove_users_from_project(users, project, callback, data)
    return data


def _remove_users_from_project(users, project: Project, callback, data: OperationResponseData):
    for user in users:
        upp: UserProjectProfile = get_proj_profile_of_user(project, user)
        if upp is None:
            data.add_error(user.id, "User not in project")
            continue
        upp.delete()
        data.add_success(user.id)
        if callback:
            callback(user, project)


def init_project_by_organization(project: Project, organization: Organization):
    # save first user to avoid unnecessary callback
    return add_users_to_project(get_users_of_org(organization), project)
