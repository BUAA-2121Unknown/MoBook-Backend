# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 16:16
# @Author  : Tony Skywalker
# @File    : notif_manager.py
#
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notif.consumers import generate_notification_consumer_token
from notif.dtos.notif_dto import NotifDto
from notif.dtos.notif_payload import NotifBasePayload
from notif.models import Notification
from shared.utils.json.exceptions import JsonSerializeException
from shared.utils.json.serializer import serialize


def dispatch_notification(target_user_id, org_id, payload: NotifBasePayload):
    try:
        payload_str = serialize(payload)
    except Exception:
        # TODO: exception swallowed
        return
    notif = Notification.create(target_user_id, org_id, payload.type, payload_str)
    notif.save()

    try:
        data = serialize(NotifDto(notif))
    except JsonSerializeException as e:
        # exception swallowed, failed to send message :(
        return

    channel_layer = get_channel_layer()
    group_id = generate_notification_consumer_token(target_user_id, org_id)
    async_to_sync(channel_layer.group_send)(group_id, {
        'type': 'notify',
        'data': data
    })
