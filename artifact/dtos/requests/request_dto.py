# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 16:22
# @Author  : Tony Skywalker
# @File    : request_dto.py
#
from typing import List

from artifact.models import ItemProperty
from shared.utils.model.model_extension import Existence
from shared.utils.validator import validate_item_name


class ItemRequestBaseDto:
    def __init__(self):
        self.projId: int = 0
        self.itemId: int = 0


class CreateItemBaseDto(ItemRequestBaseDto):
    def __init__(self):
        super().__init__()
        self.filename: str = ""

    def is_valid(self):
        return validate_item_name(self.filename)


class CreateFolderDto(CreateItemBaseDto):
    def __init__(self):
        super().__init__()

    def is_valid(self):
        return super().is_valid()


class CreateFileDto(CreateItemBaseDto):
    def __init__(self):
        super().__init__()
        self.prop: int = 0
        self.live: bool = False
        self.sibling: bool = False

    def is_valid(self):
        if not super().is_valid():
            return False
        return self.prop in ItemProperty.files()


class UpdateItemInfoDto:
    def __init__(self):
        self.projId: int = 0
        self.itemId: int = 0
        self.filename: str = ""


class UpdateItemStatusDto:
    def __init__(self):
        self.projId: int = 0
        self.status: int = 0
        self.items: List[int] = [0]

    def is_valid(self):
        return self.status in Existence.all()


class DeleteItemDto:
    def __init__(self):
        self.projId: int = 0
        self.items: List[int] = [0]


class MoveItemDto:
    def __init__(self):
        self.projId: int = 0
        self.folderId: int = 0
        self.items: List[int] = [0]


class DuplicateItemDto:
    def __init__(self):
        self.projId: int = 0
        self.itemId: int = 0


class UploadFileDto(ItemRequestBaseDto):
    def __init__(self):
        super().__init__()
        self.filename: str = ""
        self.version: int = 0


class DownloadFileDto(ItemRequestBaseDto):
    def __init__(self):
        super().__init__()
        self.token: str = ""
        self.version: int = 0

    def init(self, proj_id, item_id, token, version):
        self.projId = proj_id
        self.itemId = item_id
        self.token = token
        self.version = version
        return self


class GetVersionsDto(ItemRequestBaseDto):
    def __init__(self):
        super().__init__()


class GetItemDto(ItemRequestBaseDto):
    def __init__(self):
        super().__init__()
