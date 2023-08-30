# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/29/2023 16:56
# @Author  : Tony Skywalker
# @File    : manage.py
#
# Description:
#   Basic management of items. Creation depends on artifact implementation.
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@api_view(['POST'])
@csrf_exempt
def create_folder(request):
    """
    Create a new folder under one folder.
    """
    pass


@api_view(['POST'])
@csrf_exempt
def create_file(request):
    """
    Create a new file under one folder.
    """
    pass


@api_view(['POST'])
@csrf_exempt
def update_item_status(request):
    """
    Update the status of an item, delete or recover.
    """
    pass


@api_view(['POST'])
@csrf_exempt
def move_item(request):
    """
    Move an item to another folder.
    """
    pass
