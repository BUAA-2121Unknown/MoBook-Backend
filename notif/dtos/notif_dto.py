# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 18:38
# @Author  : Tony Skywalker
# @File    : notif_dto.py
#
from notif.models import Notification
from shared.utils.json.serializer import deserialize


class NotifDto:
    def __init__(self, notif: Notification):
        self.id = notif.id
        self.userId = notif.user_id
        self.orgId = notif.org_id
        self.type = notif.type
        self.payload = deserialize(notif.payload)
        self.timestamp = notif.timestamp
        self.status = notif.status
