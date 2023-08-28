# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 9:27
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from live.views.share import create_share_token, revoke_share_token, authorize_share_token, get_share_tokens_of_artifact

urlpatterns = [
    path('token/create', create_share_token),
    path('token/revoke', revoke_share_token),
    path('token/autho', authorize_share_token),
    path('token/all', get_share_tokens_of_artifact)
]