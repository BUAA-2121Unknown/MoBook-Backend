from django.urls import re_path

from chat import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\w+)/$', consumers.ChatMessageConsumer.as_asgi()),
    re_path(r'ws/notif/(?P<notif_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    # 用户进入团队的时候就开启他所在所有聊天的ws，
]
