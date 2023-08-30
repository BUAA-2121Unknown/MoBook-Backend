# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 16:47
# @Author  : Tony Skywalker
# @File    : error_dtos.py
#
from shared.dtos.ordinary_response_dto import NotFoundDto


class NoSuchItemDto(NotFoundDto):
    def __init__(self):
        super().__init__("No such item")
