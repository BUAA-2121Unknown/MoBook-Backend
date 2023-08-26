# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 10:48
# @Author  : Tony Skywalker
# @File    : pending_dto.py
#
from org.models import PendingStatus, PendingRecord


class UpdatePendingDto:
    def __init__(self):
        self.id: int = 0
        self.action: int = 0

    def is_valid(self):
        return self.action in PendingStatus.all()


class UpdatePendingSuccessData:
    def __init__(self, pending: PendingRecord):
        self.user: int = pending.user_status
        self.admin: int = pending.admin_status
