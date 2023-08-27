# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 11:27
# @Author  : Tony Skywalker
# @File    : update_artifact_status_dto.py
#
from typing import List

from project.models import Existence


class UpdateArtifactStatusDto:
    def __init__(self):
        self.status: int = 0
        self.artifacts: List[int] = [0]

    def is_valid(self) -> bool:
        return Existence.get_validator()(self.status)
