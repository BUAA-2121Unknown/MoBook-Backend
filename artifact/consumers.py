import json

from asgiref.sync import async_to_sync
from celery.bin.base import JSON
from channels.generic.websocket import WebsocketConsumer


class PrototypeConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.proto_id = None

    def connect(self):
        self.proto_id = self.scope['url_route']['kwargs']['proto_id']
        # Join room group
        self.proto_id = "prototype" + str(self.proto_id)
        async_to_sync(self.channel_layer.group_add)(
                self.proto_id,
                self.channel_name
        )
        print(self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.proto_id,
                self.channel_name
        )

    # 前端需要发送文件的本名和url
    def receive(self, bytes_data):
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                self.proto_id,
                {
                    "type": "back",
                    "sender_channel_name": self.channel_name,
                    "data": bytes_data
                }
        )

    # Receive message from room group
    def back(self, event):
        data = event["data"]
        if self.channel_name != event['sender_channel_name']:
            self.send(bytes_data=data)


class MouseConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.mouse_id = None

    def connect(self):
        self.mouse_id = self.scope['url_route']['kwargs']['mouse_id']
        # Join room group
        self.mouse_id = "mouse" + str(self.mouse_id)
        async_to_sync(self.channel_layer.group_add)(
                self.mouse_id,
                self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.mouse_id,
                self.channel_name
        )

    # 前端需要发送文件的本名和url
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "mouse_back"
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                self.mouse_id,
                text_data_json
        )

    # Receive message from room group
    def mouse_back(self, event):
        # if self.channel_name != event['sender_channel_name']:
        self.send(text_data=json.dumps(event))
