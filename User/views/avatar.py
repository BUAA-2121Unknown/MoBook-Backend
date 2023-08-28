# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 16:51
# @Author  : Tony Skywalker
# @File    : avatar.py
#
# Description:
#   Upload user avatar
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, InternalServerErrorDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, OkResponse, \
    InternalServerErrorResponse
from shared.utils.dir_utils import get_avatar_path, get_avatar_url
from shared.utils.file.avatar_util import save_avatar
from shared.utils.file.file_handler import parse_filename
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.validator import validate_image_name
from user.models import User


@api_view(['POST'])
@csrf_exempt
def upload_avatar(request):
    user: User = get_user_from_request(request)

    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    file = request.FILES.get('file')
    if file is None:
        return BadRequestResponse(BadRequestDto("Missing image file"))
    # if not validate_image_name(file.name):
    #     return BadRequestResponse(BadRequestDto("Invalid image type!"))
    name, ext = parse_filename(file.name)
    old_path = get_avatar_path('user', user.avatar)
    new_avatar = f"{user.id}{ext}"
    new_path = get_avatar_path('user', new_avatar)

    # save image
    try:
        save_avatar('user', old_path, new_path, file)
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to save avatar", data=e))

    user.avatar = new_avatar
    user.save()

    return OkResponse(OkDto(data={"avatar": get_avatar_url('user', user.avatar)}))
