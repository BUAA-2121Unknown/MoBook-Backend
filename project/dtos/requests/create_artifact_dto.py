# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 9:40
# @Author  : Tony Skywalker
# @File    : create_artifact_dto.py
#
from shared.utils.validator import validate_artifact_name, validate_artifact_type


class CreateArtifactDto:
    def __init__(self):
        self.projId: int = 0
        self.name: str = ""
        self.type: str = ""
        self.live: bool = False

    def is_valid(self) -> bool:
        return validate_artifact_name(self.name) and validate_artifact_type(self.type)
