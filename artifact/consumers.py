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
        async_to_sync(self.channel_layer.group_add)(
                self.proto_id,
                self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.proto_id,
                self.channel_name
        )

    # 前端需要发送文件的本名和url
    def receive(self, bytes_data):
        # type = text_data_json['type']  # 收到3就停止覆盖，直到点开
        # text = text_data_json['text']  # 如果是文件就是本名
        # file_url = text_data_json['file_url']
        # src_id = text_data_json['src_id']
        # src_name = text_data_json['src_name']
        # src_avatar_url = text_data_json['src_avatar_url']

        # 在前端给n个接收者的unread +1，但自己不应该加：如果
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                self.proto_id,
                {
                    "type": "back",
                    "data": bytes_data
                }
        )

    # Receive message from room group
    def back(self, event):
        # category = event['category']
        # text = event['text']  # 前端接受过at就忽略这条消息，访问聊天后解除
        # file_url = event['file_url']
        # src_id = event['src_id']
        # src_name = event['src_name']
        # src_avatar_url = event['src_avatar_url']
        data = event["data"]
        # 后端无法得知自己的user_id，需要交给前端判断，不给自己+1未读
        # Send message to WebSocket
        self.send(bytes_data=data
            # 'category': category,
            # 'text': text,
            # 'file_url': file_url,
            # 'src_id': src_id,
            # 'src_name': src_name,
            # 'src_avatar_url': src_avatar_url
            )
