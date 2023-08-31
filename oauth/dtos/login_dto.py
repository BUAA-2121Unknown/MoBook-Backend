# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:45
# @Author  : Tony Skywalker
# @File    : login_dto.py
from org.models import Organization
from user.dtos.org_record_dto import UserOrgRecordCompleteDto
from user.models import UserOrganizationProfile, UserOrganizationRecord, User
from user.utils.user_profile_provider import user_profile_provider_full


class LoginDto:
    def __init__(self):
        self.username: str = ""
        self.password: str = ""


class LoginSuccessDto:
    def __init__(self, user: User, token):
        self.user = user_profile_provider_full(user)
        self.token = token


class LoginSuccessCompleteDto(LoginSuccessDto):
    def __init__(self, user: User, token, record: UserOrganizationRecord, org: Organization,
                 uop: UserOrganizationProfile):
        super().__init__(user, token)
        self.lastOrg = None if record.org_id == 0 else UserOrgRecordCompleteDto(record, org, uop)
