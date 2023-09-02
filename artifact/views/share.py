# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/2/2023 14:19
# @Author  : Tony Skywalker
# @File    : share.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.requests.download_dto import DownloadContentWithTokenData, GetAllProtosWithTokenData
from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.models import Item
from artifact.utils.item_filter import filter_prototypes
from live.models import ShareToken, ShareAuth
from live.utils.token_handler import parse_share_token
from project.models import Project
from shared.dtos.ordinary_response_dto import BadRequestDto, OkDto, NotFoundDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, NotFoundResponse, UnauthorizedResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.dir_utils import get_item_path
from shared.utils.file.file_handler import load_text_file
from shared.utils.model.model_extension import first_or_default, Existence
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.token.exception import TokenException


def _validate_share_token(token):
    _, share_token = first_or_default_by_cache(ShareToken, token)
    if share_token is None:
        return None, OkResponse(OkDto(data=DownloadContentWithTokenData(
                ShareAuth.DENIED, "Missing share token")))
    if not share_token.is_active():
        return None, OkResponse(OkDto(data=DownloadContentWithTokenData(
                ShareAuth.DENIED, "Share token revoked or expired")))
    if share_token.auth == ShareAuth.DENIED:
        return None, OkResponse(OkDto(data=DownloadContentWithTokenData(
                ShareAuth.DENIED, "Permission denied")))
    return share_token, None


@api_view(['GET'])
@csrf_exempt
def download_file_content_with_token(request):
    params = parse_param(request)

    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing share token"))

    try:
        item_id, proj_id = parse_share_token(token)
    except TokenException as e:
        return BadRequestResponse(BadRequestDto("Invalid share token", data=e))
    if item_id == 0:
        item_id = parse_value(params.get('itemId'), int)
        if item_id is None:
            return BadRequestResponse(BadRequestDto("Missing itemId"))

    share_token, error_response = _validate_share_token(token)
    if share_token is None:
        return error_response

    item: Item = first_or_default(Item, id=item_id)
    if item is None:
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != proj_id:
        return UnauthorizedResponse(UnauthorizedDto("Not item of this project"))
    if not item.is_active():
        return NotFoundResponse(NotFoundDto("Shared item deleted"))

    try:
        path = get_item_path(item, item.version)
        with load_text_file(path) as f:
            content = f.read()
    except Exception as e:
        return NotFoundResponse(NotFoundDto("Shared item deleted"))

    _, proj = first_or_default_by_cache(Project, proj_id)
    return OkResponse(OkDto(data=DownloadContentWithTokenData(
            share_token.auth, "Permission granted", proj, item, content)))


@api_view(['GET'])
@csrf_exempt
def get_all_prototypes_with_token(request):
    params = parse_param(request)

    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing share token"))

    try:
        item_id, proj_id = parse_share_token(token)
    except TokenException as e:
        return BadRequestResponse(BadRequestDto("Invalid share token", data=e))
    if item_id != 0:
        return BadRequestResponse(BadRequestDto("Not a token for this"))

    share_token, error_response = _validate_share_token(token)
    if share_token is None:
        return error_response

    _, proj = first_or_default_by_cache(Project, proj_id)
    root: Item = first_or_default(Item, id=proj.root_id)
    if root is None or not root.is_active():
        return NotFoundResponse(NoSuchItemDto())
    raw_data = Item.dump_bulk(root)
    data = filter_prototypes(raw_data, Existence.ACTIVE)

    return OkResponse(OkDto(data=GetAllProtosWithTokenData(
            share_token.auth, "Permission granted", proj, data)))
