# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 20:29
# @Author  : Tony Skywalker
# @File    : version_dto.py
#
from artifact.models import FileVersion
from shared.utils.cache.cache_utils import first_or_default_by_cache
from user.dtos.user_dto import UserDto
from user.models import User


class VersionDto:
    def __init__(self, version: FileVersion):
        self.fileId = version.file_id

        self.version = version.version

        self.created = version.created
        self.updated = version.updated

        _, user = first_or_default_by_cache(User, version.user_id)
        self.user = UserDto(user)
