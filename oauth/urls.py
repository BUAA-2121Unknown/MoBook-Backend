# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:09
# @Author  : Tony Skywalker
# @File    : url.py
#

from django.urls import path

from oauth.views.login import login
from oauth.views.register import register, send_activation_link, activate
from oauth.views.token import get_jwt_token, refresh_jwt_token, revoke_jwt_token

urlpatterns = [
    path('token/get', get_jwt_token),
    path('token/refresh', refresh_jwt_token),
    path('token/revoke', revoke_jwt_token),

    path('register', register),
    path('link', send_activation_link),
    path('activate', activate),
    path('login', login),
]
