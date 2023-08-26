# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 22:30
# @Author  : Tony Skywalker
# @File    : member_profile_provider.py
#
from user.models import UserOrganizationProfile, User


def member_profile_provider(user: User, uop: UserOrganizationProfile):
