# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/26/2023 23:09
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from project.views.manage import create_project, update_project_status, duplicate_project
from project.views.profile import update_project_profile, get_project_profile

urlpatterns = [
    path('create', create_project),
    path('duplicate', duplicate_project),
    path('profile/update', update_project_profile),
    path('profile', get_project_profile),
    path('status/update', update_project_status),
]
