# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 10:16
# @Author  : Tony Skywalker
# @File    : artifact_dto.py
#
from project.dtos.models.project_dto import ProjectCompleteDto
from project.models import Artifact
from shared.utils.model.model_extension import first_or_default
from user.dtos.user_dto import UserDto
from user.models import User


class ArtifactBaseDto:
    def __init__(self, artifact: Artifact):
        self.id = artifact.id

        self.name = artifact.name
        self.type = artifact.type

        # filename is null if no file uploaded
        self.isRaw = artifact.raw
        self.filename = artifact.get_filename()

        self.created = artifact.created
        self.updated = artifact.updated

        self.isLive = artifact.live
        self.status = artifact.status

        creator = first_or_default(User, id=artifact.creator_id)
        self.creator = None if creator is None else UserDto(creator)


class ArtifactDto(ArtifactBaseDto):
    def __init__(self, artifact: Artifact):
        super().__init__(artifact)
        self.projId = artifact.proj_id


class ArtifactCompleteDto(ArtifactBaseDto):
    def __init__(self, artifact: Artifact):
        super().__init__(artifact)
        self.proj = ProjectCompleteDto(artifact.get_proj())
