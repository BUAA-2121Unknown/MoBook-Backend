# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/26/2023 23:09
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from project.views.artifact import create_artifact, update_artifact_status, update_artifact
from project.views.management import create_project, update_project_status
from project.views.profile import update_project_profile, get_artifacts_of_project

urlpatterns = [
    path('create', create_project),
    path('profile/update', update_project_profile),
    path('status/update', update_project_status),

    path('artifact/create', create_artifact),
    path('artifact/profile/update', update_artifact),
    path('artifact/status/update', update_artifact_status),

    path('artifacts', get_artifacts_of_project),
]
