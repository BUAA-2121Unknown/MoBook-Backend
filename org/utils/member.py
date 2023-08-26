# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 12:17
# @Author  : Tony Skywalker
# @File    : member.py
#
from org.models import Organization
from shared.utils.model.organization_extension import get_org_profile_of_user
from user.models import User, UserOrganizationProfile, UserAuth


def add_user_into_org(org: Organization, user: User):
    uop = get_org_profile_of_user(org, user)
    if uop is not None:
        return uop
    uop = UserOrganizationProfile.create(UserAuth.NORMAL, user, org)
    uop.save()

    return uop
