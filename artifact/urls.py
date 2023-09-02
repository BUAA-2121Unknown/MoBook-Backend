# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 21:28
# @Author  : Tony Skywalker
# @File    : urls.py
#
from django.urls import path

from artifact.views.browse import get_items_of_project, get_item, get_all_versions, get_prototypes_of_project
from artifact.views.download import download_file, download_file_content
from artifact.views.manage import create_folder, create_file, move_item, duplicate_item, delete_item
from artifact.views.share import download_file_content_with_token, get_all_prototypes_with_token
from artifact.views.update import update_item_status, update_item_name
from artifact.views.upload import upload_file, upload_file_content

urlpatterns = [
    path('create/folder', create_folder),
    path('create/file', create_file),
    path('update/status', update_item_status),
    path('update/filename', update_item_name),
    path('move', move_item),
    path('duplicate', duplicate_item),
    path('delete', delete_item),

    path('file/upload', upload_file),
    path('file/upload/content', upload_file_content),
    path('file/download', download_file),
    path('file/download/content', download_file_content),

    path('item/all', get_items_of_project),
    path('item/prototypes', get_prototypes_of_project),
    path('item/get', get_item),
    path('item/versions', get_all_versions),

    path('share/download/content', download_file_content_with_token),
    path('share/prototypes', get_all_prototypes_with_token),
]
