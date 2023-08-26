# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:44
# @Author  : Tony Skywalker
# @File    : login.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from oauth.dtos.login_dto import LoginDto, LoginSuccessDto
from shared.dtos.ordinary_response_dto import BadRequestDto, ErrorDto, OkDto, InternalServerErrorDto
from shared.response.json_response import BadRequestResponse, OkResponse, InternalServerErrorResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param
from shared.utils.token.jwt_token import generate_jwt_token
from shared.utils.token.refresh_token import generate_refresh_token
from user.models import User


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

    # generate JWT token
    try:
        token = generate_jwt_token(user.id)
        refresh_token = generate_refresh_token(user.id)
        refresh_token.save()
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate JWT token", data=e))

    response = OkResponse(OkDto(data=LoginSuccessDto(user, token)))

    # set cookies
    response.set_cookie(key="refreshToken", value=refresh_token.token, httponly=True)

    return response
