# chat/routing.py
from django.urls import re_path

from chat import consumers

websocket_urlpatterns = [
    re_path(r'ws/notification/(?P<room_name>\w+)/$', consumers.ChatConsumer),
]
