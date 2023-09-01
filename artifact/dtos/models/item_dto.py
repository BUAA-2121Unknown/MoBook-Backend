# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 16:50
# @Author  : Tony Skywalker
# @File    : item_dto.py
#
from artifact.dtos.models.version_dto import VersionDto
from artifact.models import Item
from artifact.utils.version_util import get_versions_of_file


class ItemDto:
    def __init__(self, item: Item):
        self.id = item.id

        self.name = item.name

        self.type = item.type
        self.prop = item.prop

        self.created = item.created
        self.updated = item.updated


class FolderDto(ItemDto):
    def __init__(self, item: Item):
        super().__init__(item)


class FileDto(ItemDto):
    def __init__(self, item: Item):
        super().__init__(item)
        self.version = item.version
        self.totalVersion = item.total_version


class FileCompleteDto(FileDto):
    def __init__(self, item: Item):
        super().__init__(item)
        self.versions = []
        for it in get_versions_of_file(item):
            self.versions.append(VersionDto(it))
