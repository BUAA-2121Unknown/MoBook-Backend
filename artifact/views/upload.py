# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 9:20
# @Author  : Tony Skywalker
# @File    : upload.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@api_view(['POST'])
@csrf_exempt
def upload_file(request):
    pass


@api_view(['GET'])
@csrf_exempt
def download_file(request):
    pass
