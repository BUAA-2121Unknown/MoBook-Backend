# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 21:34
# @Author  : Tony Skywalker
# @File    : cancel_org.py
#
from org.models import Organization
from user.models import UserOrganizationProfile


def cancel_organization(org: Organization):
    UserOrganizationProfile.objects.filter(org_id=org.id).delete()
    org.delete()
