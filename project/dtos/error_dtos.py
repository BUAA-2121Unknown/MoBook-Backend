# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:35
# @Author  : Tony Skywalker
# @File    : error_dtos.py
#
from shared.dtos.ordinary_response_dto import NotFoundDto


class NoSuchProjectDto(NotFoundDto):
    def __init__(self):
        super().__init__("No such project")
