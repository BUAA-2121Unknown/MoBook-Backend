# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 23:15
# @Author  : Tony Skywalker
# @File    : project_extension.py
#
from org.models import Organization
from project.models import Project


def get_projects_of_organization(organization: Organization):
    return Project.objects.filter(org_id=organization.id)
