# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/3/2023 7:18
# @Author  : Tony Skywalker
# @File    : guide.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, OkResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache, update_cached_object
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from user.models import UserGuideRecord, UserGuideType


@api_view(['GET'])
@csrf_exempt
def get_user_guide(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    typ = parse_value(params.get('type'), int)
    if typ is None:
        return BadRequestResponse(BadRequestDto("Missing type"))

    _, record = first_or_default_by_cache(UserGuideRecord, user.id)
    if record is None:
        record = UserGuideRecord.create(user.id)
        record.save()

    value = True
    if typ == UserGuideType.HOME:
        value = record.home
        record.home = True
    elif typ == UserGuideType.FILE:
        value = record.file
        record.file = True
    elif typ == UserGuideType.PROTO:
        value = record.proto
        record.proto = True
    else:
        return BadRequestResponse(BadRequestDto("Invalid type"))
    record.save()
    update_cached_object(UserGuideRecord, record.user_id, record)

    return OkResponse(OkDto(data={
        "value": value
    }))
