# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/2/2023 12:25
# @Author  : Tony Skywalker
# @File    : download_dto.py
#
from artifact.dtos.models.item_dto import FileCompleteDto
from live.dtos.authorize_dto import AuthorizeBaseData
from project.dtos.models.project_dto import ProjectCompleteDto


class DownloadFileContentSuccessData:
    def __init__(self, auth, filename, content):
        self.filename = filename
        self.content = content
        self.auth: int = auth


class DownloadContentWithTokenData(AuthorizeBaseData):
    def __init__(self, auth, msg, proj=None, item=None, content=None):
        super().__init__(auth, msg)
        self.proj = None if proj is None else ProjectCompleteDto(proj)
        self.item = None if item is None else FileCompleteDto(item)
        self.content = content


class GetAllProtosWithTokenData(AuthorizeBaseData):
    def __init__(self, auth, msg, proj=None, protos=None):
        super().__init__(auth, msg)
        self.proj = None if proj is None else ProjectCompleteDto(proj)
        self.protos = protos
        self.total = 0 if protos is None else len(protos)
