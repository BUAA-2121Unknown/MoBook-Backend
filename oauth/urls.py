# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 20:09
# @Author  : Tony Skywalker
# @File    : url.py
#

from django.urls import path

from .views import get_jwt_token, refresh_jwt_token, revoke_jwt_token

urlpatterns = [
    path('token/get', get_jwt_token),
    path('token/refresh', refresh_jwt_token),
    path('token/revoke', revoke_jwt_token),
]
