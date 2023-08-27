# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 16:16
# @Author  : Tony Skywalker
# @File    : notif_manager.py
#
from notif.models import Notification, NotifBasePayload
from org.models import Organization
from user.models import User


def dispatch_notif(user: User, org: Organization, payload: NotifBasePayload):
    org_id = None if org is None else org.id
    notif = Notification.create(user.id, org_id, payload)
    if notif is None:
        return
    notif.save()

    # TODO: trigger database update event, notification count++

# <user_id>-<org_id>/notifications