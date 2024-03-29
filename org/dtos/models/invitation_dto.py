# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 14:14
# @Author  : Tony Skywalker
# @File    : invitation_dto.py
#
from org.dtos.models.org_dto import OrganizationDto
from org.models import Invitation, Organization
from shared.utils.cache.cache_utils import first_or_default_by_cache


class InvitationBaseDto:
    def __init__(self, inv: Invitation):
        self.id = inv.id
        self.token = inv.token
        self.created = inv.created
        self.expires = inv.expires
        self.revoked = inv.revoked
        self.active = inv.is_active()
        review = inv.review


class InvitationDto(InvitationBaseDto):
    def __init__(self, inv: Invitation):
        super().__init__(inv)
        self.orgId = inv.oid


class InvitationCompleteDto(InvitationBaseDto):
    def __init__(self, inv: Invitation):
        super().__init__(inv)
        _, org = first_or_default_by_cache(Organization, inv.oid)
        self.org = None if org is None else OrganizationDto(org)
