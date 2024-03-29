# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 23:15
# @Author  : Tony Skywalker
# @File    : project_extension.py
#
from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.models import Organization
from project.dtos.requests.error_dtos import NoSuchProjectDto
from project.models import Project
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.organization_extension import get_org_with_user
from user.dtos.error_dtos import NoSuchUserDto
from user.models import User


def get_projects_of_organization(organization: Organization):
    return Project.objects.filter(org_id=organization.id)


def get_proj_and_org(project_id: int, user: User):
    if user is None:
        return None, None, NoSuchUserDto()
    _, proj = first_or_default_by_cache(Project, project_id)
    proj: Project
    if proj is None or not proj.is_active():
        return None, None, NoSuchProjectDto()
    org, _ = get_org_with_user(proj.org_id, user)
    org: Organization
    if org is None or not org.is_active():
        return None, None, NoSuchOrgDto()

    return proj, org, None
