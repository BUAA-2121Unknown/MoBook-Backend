# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 21:28
# @Author  : Tony Skywalker
# @File    : urls.py
#
from django.urls import path

from artifact.views.browse import get_items_of_project, get_item, get_all_versions
from artifact.views.manage import create_folder, create_file, update_item_status, move_item, duplicate_item, delete_item
from artifact.views.upload import upload_file, download_file

urlpatterns = [
    path('create/folder', create_folder),
    path('create/file', create_file),
    path('update', update_item_status),
    path('move', move_item),
    path('duplicate', duplicate_item),
    path('delete', delete_item),

    path('file/upload', upload_file),
    path('file/download', download_file),

    path('item/all', get_items_of_project),
    path('item/get', get_item),
    path('item/versions', get_all_versions),
]
