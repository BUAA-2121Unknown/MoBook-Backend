# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 22:18
# @Author  : Tony Skywalker
# @File    : update_member_profile_dto.py
#
from shared.utils.validator import validate_member_nickname
from user.models import UserAuth


class MemberProfileData:
    def __init__(self):
        self.nickname: str = ""

    def is_valid(self):
        return validate_member_nickname(self.nickname)


class UpdateMemberProfileDto:
    def __init__(self):
        self.orgId: int = 0
        self.userId: int = 0
        self.profile: MemberProfileData = MemberProfileData()
        self.auth: int = 0

    def is_valid(self) -> bool:
        return self.auth in UserAuth.all() and self.profile.is_valid()
