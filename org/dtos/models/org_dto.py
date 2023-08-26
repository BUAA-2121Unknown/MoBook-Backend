# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 20:40
# @Author  : Tony Skywalker
# @File    : org_dto.py
#
from org.models import Organization


class OrganizationDto:
    def __init__(self, org: Organization):
        self.id = org.id
        self.name = org.name
        self.description = org.description
        self.chatId = org.chat_id
