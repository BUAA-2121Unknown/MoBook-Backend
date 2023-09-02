# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 9:02
# @Author  : Tony Skywalker
# @File    : authorize_dto.py
#
from artifact.models import Item
from project.models import Project


class AuthorizeData:
    def __init__(self, auth: int, msg: str):
        self.auth = auth
        self.message = msg


class AuthorizeSuccessData(AuthorizeData):
    def __init__(self, auth, proj: Project, item: Item):
        super().__init__(auth, "Permission granted")
        self.projId = proj.id
        self.itemId = None if item is None else item.id


class AuthorizeBaseData:
    def __init__(self, auth: int, msg: str):
        self.auth = auth
        self.message = msg
