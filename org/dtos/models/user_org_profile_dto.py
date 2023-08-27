# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 22:31
# @Author  : Tony Skywalker
# @File    : user_org_profile_dto.py
#
from user.dtos.user_dto import UserDto
from user.models import UserOrganizationProfile, User


class MemberDto:
    def __init__(self, uop: UserOrganizationProfile):
        self.orgId = uop.org_id
        self.nickname = uop.nickname
        self.auth = uop.auth


# UserOrganizationProfileDto
class UopDto:
    def __init__(self, user: User, uop: UserOrganizationProfile):
        self.user = UserDto(user)
        self.uop = MemberDto(uop)
