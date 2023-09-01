# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 14:58
# @Author  : Tony Skywalker
# @File    : consumers.py
#
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


def generate_notification_consumer_token(uid, oid) -> str:
    # return to_base64_token(f'{uid}-{"default" if oid is None else oid}')
    return f'{uid}-{"default" if oid is None else oid}'


class NotificationConsumer(WebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.group_token = None

    def connect(self):
        user_id = self.scope['url_route']['kwargs']['user_id']
        org_id = self.scope['url_route']['kwargs']['org_id']

        # TODO: check permissions

        self.group_token = generate_notification_consumer_token(user_id, org_id)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
                self.group_token,
                self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                self.group_token,
                self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        pass

    # Receive message from room group
    def notify(self, event):
        # Send message to WebSocket
        data = event['data']
        # self.send(json=data)
        self.send(text_data=data)
