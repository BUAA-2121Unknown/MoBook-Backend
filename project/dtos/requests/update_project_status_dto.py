# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:49
# @Author  : Tony Skywalker
# @File    : update_project_status_dto.py
#
from typing import List

from project.models import Existence


class UpdateProjectStatusDto:
    def __init__(self):
        self.status: int = 0
        self.projects: List[int] = [0]

    def is_valid(self) -> bool:
        return Existence.get_validator()(self.status)
