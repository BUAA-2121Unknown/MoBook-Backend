# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 9:27
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from live.views.browse import get_share_token, preview_share_token
from live.views.share import open_share_token, revoke_share_token, delete_share_token, authorize_share_token

urlpatterns = [
    path('token/open', open_share_token),
    path('token/revoke', revoke_share_token),
    path('token/delete', delete_share_token),
    path('token/auth', authorize_share_token),
    path('token/get', get_share_token),
    path('token/preview', preview_share_token)
]
