import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from message.models import Message


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None

    def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.chat_id,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Message.objects.create(user=self.scope['user'], message=message, group_name=self.room_group_name
        # image_path = image_path, file_path = file_path, type = type, src_id = src_id, dst_id = dst_id, chat_id = chat_id, timestamp = timestamp)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
            self.chat_id,
            {
                'type': 'chat_message',  # function
                'message': message,
                'username': username

            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
