import json

from asgiref.sync import async_to_sync
from celery.bin.base import JSON
from channels.generic.websocket import WebsocketConsumer
from channels.layers import channel_layers


class ChatMessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None

    def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        async_to_sync(self.channel_layer.group_add)(
                self.chat_id,
                self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                self.chat_id,
                self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "chat_message"
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                self.chat_id,
                text_data_json
        )
        chats_channel_layer = channel_layers[ChatsConsumer.channel_layer_alias]
        async_to_sync(chats_channel_layer.group_send)(

        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(
            event
        ))


class ChatsConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.org_id = None
        self.user_id = None

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.org_id = self.scope['url_route']['kwargs']['org_id']
        async_to_sync(self.channel_layer.group_add)(
                str(self.user_id) + str(self.org_id),
                self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                str(self.user_id) + str(self.org_id),
                self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "chat_message"
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                str(self.user_id) + str(self.org_id),
                text_data_json
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(
            event
        ))
