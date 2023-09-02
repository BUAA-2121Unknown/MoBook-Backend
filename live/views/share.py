# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 3:10
# @Author  : Tony Skywalker
# @File    : live.py
#
from datetime import timedelta

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.models import Item
from live.dtos.authorize_dto import AuthorizeData
from live.dtos.open_share_token_dto import OpenShareTokenDto
from live.dtos.share_token_dto import ShareTokenDto
from live.models import ShareToken, ShareAuth
from live.utils.authorize import authorize_share_token_aux
from live.utils.token_handler import generate_share_token, update_or_create_share_token, parse_share_token
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, NotFoundDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache, delete_cached_object, update_cached_object
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.token.exception import TokenException


@api_view(['POST'])
@csrf_exempt
def open_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: OpenShareTokenDto = deserialize(params, OpenShareTokenDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto())
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    # get item
    if dto.itemId == 0:
        item = None
    else:
        item: Item = first_or_default(Item, id=dto.itemId)
        if item is None:
            return NotFoundResponse(NotFoundDto("Item not found"))
        if item.is_dir():
            return ForbiddenResponse(ForbiddenDto("Sharing file is not supported yet"))

    # get project
    proj, org, error = get_proj_and_org(dto.projId, user)
    if error is not None:
        return NotFoundResponse(error)

    # verify item
    if item is not None and item.proj_id != proj.id:
        return BadRequestResponse(BadRequestDto("Item not in project"))

    # create or update share token
    token = generate_share_token(dto.itemId, dto.projId)
    created = timezone.now()
    expires = (created + timedelta(days=dto.expires)) if dto.expires > 0 else None
    share_token = update_or_create_share_token(token, created, expires, dto.auth)

    return OkResponse(OkDto(data=ShareTokenDto(share_token)))


@api_view(['POST'])
@csrf_exempt
def revoke_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    # verify share token
    item_id, proj_id = parse_share_token(token)
    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return NotFoundResponse(error)

    _, share_token = first_or_default_by_cache(ShareToken, token)
    if share_token is None:
        return NotFoundResponse(NotFoundDto("Token not found"))
    if not share_token.is_active():
        return OkResponse(OkDto("Token not active already"))

    # simply delete share token
    share_token.revoked = timezone.now()
    share_token.save()
    update_cached_object(ShareToken, token, share_token)

    return OkResponse(OkDto("Token revoked", data=ShareTokenDto(share_token)))


@api_view(['POST'])
@csrf_exempt
def delete_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    # verify share token
    try:
        item_id, proj_id = parse_share_token(token)
    except TokenException as e:
        return BadRequestResponse(BadRequestDto("Invalid token", data=e))
    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return NotFoundResponse(error)

    _, share_token = first_or_default_by_cache(ShareToken, token)
    if share_token is None:
        return NotFoundResponse(NotFoundDto(data=AuthorizeData(ShareAuth.DENIED, "Invalid token")))

    # simply delete share token
    delete_cached_object(ShareToken, token)
    share_token.delete()

    return OkResponse(OkDto("Token revoked", data=ShareTokenDto(share_token)))


@api_view(['GET'])
@csrf_exempt
def authorize_share_token(request):
    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    user = get_user_from_request(request)
    data = authorize_share_token_aux(token, user)

    return OkResponse(OkDto(data=data))
