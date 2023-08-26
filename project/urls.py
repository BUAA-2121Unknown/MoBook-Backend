# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/26/2023 23:09
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from project.views.management import create_project, update_project_status
from project.views.profile import update_project_profile

urlpatterns = [
    path('manage/create', create_project),
    path('manage/status', update_project_status),

    path('profile/update', update_project_profile)
]
