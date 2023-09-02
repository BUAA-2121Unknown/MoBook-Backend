# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 17:59
# @Author  : Tony Skywalker
# @File    : browse.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from live.dtos.share_token_dto import ShareTokenDto
from live.models import ShareToken
from live.utils.token_handler import generate_share_token
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, NotFoundDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['GET'])
@csrf_exempt
def get_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    item_id = parse_value(params.get('itemId'), int)
    proj_id = parse_value(params.get('projId'), int)
    if item_id is None or proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing itemId or projId"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return NotFoundResponse(error)

    token = generate_share_token(item_id, proj_id)
    _, share_token = first_or_default_by_cache(ShareToken, token)

    return OkResponse(OkDto(data={
        "token": None if share_token is None else ShareTokenDto(share_token)
    }))


@api_view(['POST'])
@csrf_exempt
def preview_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    item_id = parse_value(params.get('itemId'), int)
    proj_id = parse_value(params.get('projId'), int)
    if item_id is None or proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing itemId or projId"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return NotFoundResponse(error)

    token = generate_share_token(item_id, proj_id)
    share_token: ShareToken = first_or_default_by_cache(ShareToken, token)

    if share_token is None or not share_token.is_active():
        return NotFoundResponse(NotFoundDto("No such share token"))

    return OkResponse(OkDto(data=ShareTokenDto(share_token)))
