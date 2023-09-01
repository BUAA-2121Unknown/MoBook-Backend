from django.urls import re_path

from artifact import consumers

websocket_urlpatterns = [
    re_path(r'prototype/(?P<proto_id>\w+)/$', consumers.PrototypeConsumer.as_asgi()),
    re_path(r'mouse/(?P<mouse_id>\w+)/$', consumers.MouseConsumer.as_asgi()),
    # 用户进入团队的时候就开启他所在所有聊天的ws，
]
