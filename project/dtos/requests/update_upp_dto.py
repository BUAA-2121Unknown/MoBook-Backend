# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 20:40
# @Author  : Tony Skywalker
# @File    : update_upp_dto.py
#

class UpdateUserProjectProfileDto:
    def __init__(self):
        self.projId: int = 0
        self.userId: int = 0
        self.role: str = ""
