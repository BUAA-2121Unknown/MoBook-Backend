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
        self.id = None if proj is None else proj.id
        self.name = None if proj is None else proj.name
        self.description = None if proj is None else proj.description
        self.created = None if proj is None else proj.created
        self.updated = None if proj is None else proj.updated
        self.status = None if proj is None else proj.status


class ProjectDto(ProjectBaseDto):
    def __init__(self, proj: Project):
        super().__init__(proj)
        self.orgId = None if proj is None else proj.org_id


class ProjectCompleteDto(ProjectBaseDto):
    def __init__(self, proj: Project, org: Organization = None):
        super().__init__(proj)
        self.org = OrganizationDto(proj.get_org() if org is None else org)
