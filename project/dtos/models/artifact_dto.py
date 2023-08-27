# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 10:16
# @Author  : Tony Skywalker
# @File    : artifact_dto.py
#
from project.dtos.models.project_dto import ProjectCompleteDto
from project.models import Artifact


class ArtifactBaseDto:
    def __init__(self, artifact: Artifact):
        self.id = artifact.id

        self.name = artifact.name
        self.type = artifact.type

        # external means whether server has the file or not
        self.external = artifact.external

        self.created = artifact.created
        self.updated = artifact.updated

        self.status = artifact.status


class ArtifactDto(ArtifactBaseDto):
    def __init__(self, artifact: Artifact):
        super().__init__(artifact)
        self.projId = artifact.proj_id


class ArtifactCompleteDto(ArtifactBaseDto):
    def __init__(self, artifact: Artifact):
        super().__init__(artifact)
        self.proj = ProjectCompleteDto(artifact.get_proj())
