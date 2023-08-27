# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:49
# @Author  : Tony Skywalker
# @File    : update_project_status_dto.py
#
from project.models import Existence


class UpdateProjectStatusDto:
    def __init__(self, project_id: int, status: int):
        self.projId = project_id
        self.status = status

    def is_valid(self) -> bool:
        return self.status in Existence.all()
