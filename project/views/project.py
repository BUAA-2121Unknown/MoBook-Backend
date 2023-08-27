# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/27/2023 9:30
# @Author  : Tony Skywalker
# @File    : project.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@api_view(['POST'])
@csrf_exempt
def create_artifact(request):
    pass


@api_view(['POST'])
@csrf_exempt
def update_artifact(request):
    pass


@api_view(['POST'])
@csrf_exempt
def update_artifact_status(request):
    pass
