# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 8:52
# @Author  : Tony Skywalker
# @File    : share_token_dto.py
#
from artifact.dtos.models.item_dto import FileDto, FolderDto
from artifact.models import Item
from live.models import ShareToken
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.dtos.models.project_dto import ProjectDto
from project.models import Project
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import first_or_default


class ShareTokenBaseDto:
    def __init__(self, token: ShareToken):
        self.id = token.id

        self.token = token.token

        self.created = token.created
        self.expires = token.expires
        self.revoked = token.revoked
        self.active = token.is_active()

        self.auth = token.auth
        self.orgOnly = token.org_only


class ShareTokenDto(ShareTokenBaseDto):
    def __init__(self, token: ShareToken):
        super(ShareTokenDto, self).__init__(token)
        self.artId = token.item_id
        self.projId = token.proj_id
        self.orgId = token.org_id


class ShareTokenCompleteDto(ShareTokenBaseDto):
    def __init__(self, token: ShareToken):
        super(ShareTokenCompleteDto, self).__init__(token)
        item = first_or_default(Item, id=token.item_id)
        self.item = None if item is None else (FolderDto(item) if item.is_dir() else FileDto(item))
        _, proj = first_or_default_by_cache(Project, token.proj_id)
        self.project = ProjectDto(proj)
        org = first_or_default(Organization, id=token.org_id)
        self.org = None if org is None else OrganizationDto(org)
