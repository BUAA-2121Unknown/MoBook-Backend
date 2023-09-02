import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


def generate_prototype_consumer_token(proto_id) -> str:
    return f"proto-{proto_id}"


class PrototypeConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_token = None

    def connect(self):
        proto_id = self.scope['url_route']['kwargs']['proto_id']
        self.group_token = generate_prototype_consumer_token(proto_id)

        # Join room group
        self.proto_id = "prototype" + str(self.proto_id)
        async_to_sync(self.channel_layer.group_add)(
                self.group_token,
                self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.group_token,
                self.channel_name
        )

    # 前端需要发送文件的本名和url
    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
                self.group_token,
                {
                    "type": "back",
                    "sender_channel_name": self.channel_name,
                    "data": bytes_data
                }
        )

    # Receive message from room group
    def back(self, event):
        data = event.get("data", None)
        if data is not None:
            if self.channel_name != event['sender_channel_name']:
                self.send(bytes_data=data)


def generate_moues_consumer_token(mouse_id) -> str:
    return f"mouse-{mouse_id}"


class MouseConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_token = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.mouse_id = None

    def connect(self):
        mouse_id = self.scope['url_route']['kwargs']['mouse_id']
        self.group_token = generate_moues_consumer_token(mouse_id)

        # Join room group
        self.mouse_id = "mouse" + str(self.mouse_id)
        async_to_sync(self.channel_layer.group_add)(
                self.group_token,
                self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.group_token,
                self.channel_name
        )

    # 前端需要发送文件的本名和url
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "back"
        async_to_sync(self.channel_layer.group_send)(self.group_token, {
            "type": "back",
            "text": text_data_json
        })

        # Receive message from room group

    def back(self, event):
        # if self.channel_name != event['sender_channel_name']:
        self.send(text_data=event.get("text", None))
