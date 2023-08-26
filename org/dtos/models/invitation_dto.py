# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 14:14
# @Author  : Tony Skywalker
# @File    : invitation_dto.py
#
from org.dtos.models.org_dto import OrganizationDto
from org.models import Invitation, Organization
from shared.utils.model.model_extension import first_or_default


class InvitationDto:
    def __init__(self, inv: Invitation):
        self.id = inv.id
        self.token = inv.token
        self.created = inv.created
        self.expires = inv.expires
        self.revoked = inv.revoked
        org = first_or_default(Organization, id=inv.oid)
        self.org = None if org is None else OrganizationDto(org)
        review = inv.review
