# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:44
# @Author  : Tony Skywalker
# @File    : login.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from user.models import User
from oauth.dtos.login_dto import LoginDto
from shared.dtos.OrdinaryResponseDto import BadRequestDto, ErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def login(request):
    params = parse_param(request)
    try:
        dto: LoginDto = deserialize(params, LoginDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto("Bad parameter"))

    user: User = first_or_default(User, username=dto.username)
    if user is None:
        return OkResponse(ErrorDto(1000021, "Not registered"))
    if not user.activated:
        return OkResponse(ErrorDto(1000022, "Not activated"))

    return OkResponse(OkDto(data={'id': user.id}))
