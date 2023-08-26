# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:26
# @Author  : Tony Skywalker
# @File    : project_dto.py
#
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.models import Project


class ProjectBaseDto:
    def __init__(self, proj: Project):
        self.id = proj.id
        self.name = proj.name
        self.description = proj.description


class ProjectDto(ProjectBaseDto):
    def __init__(self, proj: Project):
        super().__init__(proj)
        self.orgId = proj.org_id


class ProjectCompleteDto(ProjectBaseDto):
    def __init__(self, proj: Project, org: Organization = None):
        super().__init__(proj)
        self.org = OrganizationDto(proj.get_org() if org is None else org)
