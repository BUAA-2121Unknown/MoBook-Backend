import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from message.models import Message


class ChatMessageConsumer(WebsocketConsumer):
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

    # 前端需要发送文件的本名和url
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        text = text_data_json['text']  # 如果是文件就是本名
        file_url = text_data_json['file_url']
        src_id = text_data_json['src_id']
        src_name = text_data_json['src_name']
        src_avatar_url = text_data_json['src_avatar_url']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
            self.chat_id,
            {
                'type': 'chat_message',  # function
                'category': type,
                'text': text,
                'file_url': file_url,
                'src_id': src_id,
                'src_name': src_name,
                'src_avatar_url': src_avatar_url
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        category = event['category']
        text = event['text']  # 前端接受过at就忽略这条消息，访问聊天后解除
        file_url = event['file_url']
        src_id = event['src_id']
        src_name = event['src_name']
        src_avatar_url = event['src_avatar_url']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'category': category,
            'text': text,
            'file_url': file_url,
            'src_id': src_id,
            'src_name': src_name,
            'src_avatar_url': src_avatar_url
        }))


class NotificationConsumer(WebsocketConsumer):

    async def connect(self):
        await self.accept()

    def disconnect(self, close_code):
        pass

    # 前端需要发送文件的本名和url
    def receive(self, text_data):
        pass

    # Receive message from room group
    def notify(self, event):

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': event['data']
        }))
