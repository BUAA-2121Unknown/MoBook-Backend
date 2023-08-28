# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 8:52
# @Author  : Tony Skywalker
# @File    : share_token_dto.py
#
from live.models import ShareToken
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.dtos.models.artifact_dto import ArtifactDto
from project.dtos.models.project_dto import ProjectDto
from project.models import Artifact, Project
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
        self.artId = token.art_id
        self.projId = token.proj_id
        self.orgId = token.org_id


class ShareTokenCompleteDto(ShareTokenBaseDto):
    def __init__(self, token: ShareToken):
        super(ShareTokenCompleteDto, self).__init__(token)
        art = first_or_default(Artifact, id=token.art_id)
        self.artifact = None if art is None else ArtifactDto(art)
        proj = first_or_default(Project, id=token.proj_id)
        self.project = None if proj is None else ProjectDto(proj)
        org = first_or_default(Organization, id=token.org_id)
        self.org = None if org is None else OrganizationDto(org)
