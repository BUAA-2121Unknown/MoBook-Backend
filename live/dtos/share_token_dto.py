# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 8:52
# @Author  : Tony Skywalker
# @File    : share_token_dto.py
#
from artifact.dtos.models.item_dto import FileDto, FolderDto
from artifact.models import Item
from live.models import ShareToken
from live.utils.token_handler import parse_share_token
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.dtos.models.project_dto import ProjectDto
from project.models import Project
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import first_or_default


class ShareTokenBaseDto:
    def __init__(self, token: ShareToken):
        self.token = token.token

        self.created = token.created
        self.expires = token.expires
        self.revoked = token.revoked
        self.active = token.is_active()

        self.auth = token.auth
        # self.orgOnly = token.org_only


class ShareTokenDto(ShareTokenBaseDto):
    def __init__(self, token: ShareToken):
        super(ShareTokenDto, self).__init__(token)
        item_id, proj_id = parse_share_token(token.token)
        self.itemId = item_id
        self.projId = proj_id


class ShareTokenCompleteDto(ShareTokenBaseDto):
    def __init__(self, token: ShareToken):
        super(ShareTokenCompleteDto, self).__init__(token)
        item_id, proj_id = parse_share_token(token.token)
        item = first_or_default(Item, id=item_id)
        self.item = None if item is None else (FolderDto(item) if item.is_dir() else FileDto(item))
        _, proj = first_or_default_by_cache(Project, proj_id)
        proj: Project
        self.project = ProjectDto(proj)
        _, org = first_or_default_by_cache(Organization, proj.org_id)
        self.org = None if org is None else OrganizationDto(org)
