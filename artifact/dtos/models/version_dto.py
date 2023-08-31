# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 20:29
# @Author  : Tony Skywalker
# @File    : version_dto.py
#
from artifact.models import FileVersion
from shared.utils.model.model_extension import first_or_default
from user.dtos.user_dto import UserDto
from user.models import User


class VersionDto:
    def __init__(self, version: FileVersion):
        self.fileId = version.file_id

        self.version = version.version

        self.created = version.created
        self.updated = version.updated

        self.user = UserDto(first_or_default(User, id=version.user_id))
