# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 9:51
# @Author  : Tony Skywalker
# @File    : org_record_dto.py
#
from org.dtos.models.org_dto import OrgWithAuthDto
from org.models import Organization
from user.models import UserOrganizationRecord, UserOrganizationProfile


class UserOrgRecordBaseDto:
    def __init__(self, record: UserOrganizationRecord):
        self.lastAccessed = record.last_accessed


class UserOrgRecordDto(UserOrgRecordBaseDto):
    def __init__(self, record: UserOrganizationRecord):
        super().__init__(record)
        self.lastOrgId = record.org_id


class UserOrgRecordCompleteDto(UserOrgRecordBaseDto):
    def __init__(self, record: UserOrganizationRecord, org: Organization, uop: UserOrganizationProfile):
        super().__init__(record)
        self.lastOrg = None if org is None else OrgWithAuthDto(org, uop)
