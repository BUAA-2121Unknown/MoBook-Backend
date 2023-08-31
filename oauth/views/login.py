# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:44
# @Author  : Tony Skywalker
# @File    : login.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from oauth.dtos.login_dto import LoginDto, LoginSuccessDto, LoginSuccessCompleteDto
from oauth.utils.gererate_jwt_token_pair import generate_jwt_token_pair
from shared.dtos.ordinary_response_dto import BadRequestDto, ErrorDto, OkDto, InternalServerErrorDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, InternalServerErrorResponse, \
    UnauthorizedResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_last_org_with_uop
from shared.utils.parameter.parameter import parse_param
from shared.utils.token.exception import TokenException
from shared.utils.token.password import verify_password
from user.models import User, UserOrganizationRecord


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

    if not verify_password(dto.password, user.password):
        return UnauthorizedResponse(UnauthorizedDto("Wrong password"))

    # generate JWT token
    # create JWT token and refresh token
    try:
        jwt_token, refresh_token = generate_jwt_token_pair(user.id)
    except TokenException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate JWT token", data=e))

    record, org, uop = get_last_org_with_uop(user)

    response = OkResponse(OkDto(data=LoginSuccessCompleteDto(user, jwt_token, record, org, uop)))

    # set cookies
    response.set_cookie(key="refreshToken", value=refresh_token.token, httponly=True)


    return response
