# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 14:57
# @Author  : Tony Skywalker
# @File    : routing.py
#


from django.urls import re_path

from notif.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notif/(?P<user_id>\w+)/(?P<org_id>\w+)/$', NotificationConsumer.as_asgi()),
]
