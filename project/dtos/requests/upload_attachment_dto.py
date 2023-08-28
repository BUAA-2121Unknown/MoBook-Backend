# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 12:16
# @Author  : Tony Skywalker
# @File    : upload_attachment_dto.py
#
from project.models import Artifact


class UploadContentAttachmentDto:
    def __init__(self):
        self.artId: int = 0
        self.filename: str = ""  # with extension
        self.content: str = ""


class DownloadContentAttachmentSuccessData:
    def __init__(self, art: Artifact, filename: str, content: str):
        self.artId: int = art.id
        self.filename: str = filename
        self.content: str = content
