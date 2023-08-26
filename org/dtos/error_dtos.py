# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 20:20
# @Author  : Tony Skywalker
# @File    : error_dtos.py
#
from shared.dtos.OrdinaryResponseDto import NotFoundDto


class NoSuchOrgDto(NotFoundDto):
    def __init__(self):
        super().__init__("No such organization")
