# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 19:40
# @Author  : Tony Skywalker
# @File    : user_dto.py
#
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.organization_extension import get_org_with_user
from user.models import User, UserOrganizationProfile


class UserDto:
    def __init__(self, user: User):
        self.id = None if user is None else user.id
        self.username = None if user is None else user.username
        self.name = None if user is None else user.name
        self.avatarUrl = None if user is None else get_avatar_url('user', user.avatar)
        self.email = None if user is None else user.email


class UserWithNicknameDto:
    def __init__(self, user: User, org_id):
        self.id = None if user is None else user.id
        self.username = None if user is None else user.username

        org, uop = get_org_with_user(org_id, user)
        uop: UserOrganizationProfile
        self.name = user.username if uop is None else uop.nickname

        self.avatarUrl = None if user is None else get_avatar_url('user', user.avatar)
        self.email = None if user is None else user.email
