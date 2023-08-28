# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/26/2023 23:09
# @Author  : Tony Skywalker
# @File    : urls.py
#

from django.urls import path

from project.views.artifact import create_artifact, update_artifact_status, update_artifact, get_artifacts_of_project, \
    get_artifact
from project.views.attachment import upload_artifact_attachment, download_artifact_attachment, \
    download_artifact_content_attachment, upload_artifact_content_attachment
from project.views.manage import create_project, update_project_status
from project.views.member import update_project_member_profile, get_project_members
from project.views.profile import update_project_profile

urlpatterns = [
    path('create', create_project),
    path('profile/update', update_project_profile),
    path('status/update', update_project_status),

    path('artifact/create', create_artifact),
    path('artifact/status/update', update_artifact_status),
    path('artifact/profile/update', update_artifact),

    path('artifact/file/upload', upload_artifact_attachment),
    path('artifact/file/upload/content', upload_artifact_content_attachment),
    path('artifact/file/download', download_artifact_attachment),
    path('artifact/file/download/content', download_artifact_content_attachment),

    path('artifacts', get_artifacts_of_project),
    path('artifact/profile', get_artifact),

    path('member/profile/update', update_project_member_profile),
    path('members/', get_project_members),
]
