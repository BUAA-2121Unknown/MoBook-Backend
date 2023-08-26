# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 18:34
# @Author  : Tony Skywalker
# @File    : get_notif_dto.py
#
from typing import List

from notif.models import NotifStatus
from shared.dtos.paged_request_dto import PagedRequestDto


class GetNotifDto(PagedRequestDto):
    def __init__(self):
        super().__init__()
        self.orgId: int = 0
        self.status: List[int] = [0]


class EditNotifDto:
    def __init__(self):
        self.status: int = 0
        self.notifications: List[int] = [0]

    def is_valid(self):
        return self.status in NotifStatus.all()
