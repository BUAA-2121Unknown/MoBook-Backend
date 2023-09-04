import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import channel_layers

from user.models import UserChatRelation


class ChatMessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None
        self.group_name = None

    def connect(self):
        self.group_name = "chat" + str(self.scope['url_route']['kwargs']['chat_id'])
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "chat_message"

        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
            self.group_name,
            text_data_json
        )
        # 获得聊天室里面的人
        # 哪个组织
        print(text_data_json["type"])
    def chat_message(self, event):
        self.send(text_data=json.dumps(
                event
        ))


class ChatsConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.org_id = None
        self.user_id = None
        self.group_name = None

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.org_id = self.scope['url_route']['kwargs']['org_id']
        self.group_name = "chats" + str(self.user_id) + str(self.org_id)  # TODO:没加组织
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        text_data_json["type"] = "chats"
        async_to_sync(self.channel_layer.group_send)(  # 按照接口需求
            self.group_name,
            text_data_json
        )

    def chats(self, event):
        self.send(text_data=json.dumps(
                event
        ))
