# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 18:05
# @Author  : Tony Skywalker
# @File    : profile.py
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, OkResponse
from shared.utils.cache.cache_utils import update_cached_object, first_or_default_by_cache
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_username, validate_name
from user.dtos.error_dtos import UsernameOccupiedDto, NoSuchUserDto
from user.models import User
from user.utils.user_profile_provider import user_profile_provider_full, user_profile_provider_simple


@api_view(['POST'])
@csrf_exempt
def update_user_profile(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    username = parse_value(params.get('username'), str)
    if username is not None and username != user.username:
        if not validate_username(username):
            return BadRequestResponse(BadRequestDto("Invalid username"))
        if first_or_default(User, username__exact=username) is not None:
            return OkResponse(UsernameOccupiedDto())
        user.username = username
    name = parse_value(params.get('name'), str)
    if name is not None and name != user.name:
        if not validate_name(name):
            return BadRequestResponse(BadRequestDto("Invalid name"))
        user.name = name
    user.save()

    update_cached_object(User, user.id, user)

    return OkResponse(OkDto(data={
        "username": user.username,
        "name": user.name
    }))


@api_view(['GET'])
@csrf_exempt
def get_user_profile(request):
    params = parse_param(request)

    uid = parse_value(params.get('id'), int)
    if uid is None:
        return BadRequestResponse(BadRequestDto("Missing id"))
    _, user = first_or_default_by_cache(User, uid)
    # user = first_or_default(User, id=uid)
    if user is None:
        return BadRequestResponse(NoSuchUserDto())

    if params.get('mode', None) == 'full':
        provider = user_profile_provider_full
    else:
        provider = user_profile_provider_simple

    data = provider(user)

    return OkResponse(OkDto(data=data))
