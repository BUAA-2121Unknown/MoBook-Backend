# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 21:51
# @Author  : Tony Skywalker
# @File    : create_project_dto.py
#

class CreateProjectDto:
    def __init__(self):
        self.orgId: int = 0
        self.name: str = ""
        self.description: str = ""
