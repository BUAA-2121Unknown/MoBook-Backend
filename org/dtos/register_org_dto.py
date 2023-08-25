# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 21:16
# @Author  : Tony Skywalker
# @File    : register_org_dto.py
#
from shared.utils.validator import validate_org_name, validate_org_descr


class RegisterOrgDto:
    def __init__(self):
        self.name: str = ""
        self.description: str = ""

    def is_valid(self):
        return validate_org_name(self.name) and validate_org_descr(self.description)
