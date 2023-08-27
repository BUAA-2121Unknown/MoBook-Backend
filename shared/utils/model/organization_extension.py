# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 20:00
# @Author  : Tony Skywalker
# @File    : organization_extension.py
#
from org.models import Organization
from shared.utils.model.model_extension import first_or_default
from user.models import User, UserOrganizationProfile, UserAuth


def get_org_profile_of_user(org: Organization, user: User):
    # User Organization Profile
    return first_or_default(UserOrganizationProfile, org_id=org.id, user_id=user.id)


def _get_org_and_profile_of_user(oid, user: User):
    if oid is None or user is None:
        return None, None

    org = first_or_default(Organization, id=oid)
    if org is None:
        return None, None
    uop = get_org_profile_of_user(org, user)
    if uop is None:
        return None, None
    return org, uop


def get_org_of_user(oid, user: User):
    org, oup = _get_org_and_profile_of_user(oid, user)
    if org is None:
        return None, None
    oup: UserOrganizationProfile
    if oup.auth == UserAuth.CREATOR:
        return org, oup
    return None, None


def get_org_managed_by_user(oid, user: User):
    org, oup = _get_org_and_profile_of_user(oid, user)
    if org is None:
        return None, None
    oup: UserOrganizationProfile
    if oup.auth == UserAuth.CREATOR or oup.auth == UserAuth.ADMIN:
        return org, oup
    return None, None


def get_org_with_user(oid, user: User):
    org, uop = _get_org_and_profile_of_user(oid, user)
    return org, uop
