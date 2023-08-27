# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 20:39
# @Author  : Tony Skywalker
# @File    : org_profile_provider.py
#
from org.dtos.models.org_dto import OrganizationDto, OrgWithAuthDto
from org.models import Organization


def org_profile_provider_full(org: Organization):
    return OrgWithAuthDto(org)


def org_profile_provider_simple(org: Organization):
    return OrganizationDto(org)
