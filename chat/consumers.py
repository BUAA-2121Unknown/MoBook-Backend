import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


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
        print("hey")
        text_data_json = json.loads(text_data)
        # type = text_data_json['type']  # 收到3就停止覆盖，直到点开
        # text = text_data_json['text']  # 如果是文件就是本名
        # file_url = text_data_json['file_url']
        # src_id = text_data_json['src_id']
        # src_name = text_data_json['src_name']
        # src_avatar_url = text_data_json['src_avatar_url']

        # 在前端给n个接收者的unread +1，但自己不应该加：如果

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
                self.chat_id,
                {
                    'type': 'chat_message',  # function
                    # 'category': type,
                    # 'text': text,
                    # 'file_url': file_url,
                    # 'src_id': src_id,
                    # 'src_name': src_name,
                    # 'src_avatar_url': src_avatar_url
                    'content': text_data_json['content']
                }
        )

    # Receive message from room group
    def chat_message(self, event):
        # category = event['category']
        # text = event['text']  # 前端接受过at就忽略这条消息，访问聊天后解除
        # file_url = event['file_url']
        # src_id = event['src_id']
        # src_name = event['src_name']
        # src_avatar_url = event['src_avatar_url']

        # 后端无法得知自己的user_id，需要交给前端判断，不给自己+1未读
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            # 'category': category,
            # 'text': text,
            # 'file_url': file_url,
            # 'src_id': src_id,
            # 'src_name': src_name,
            # 'src_avatar_url': src_avatar_url
            'content': event['content']
        }))
