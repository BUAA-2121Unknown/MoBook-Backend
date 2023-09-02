# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/2/2023 0:22
# @Author  : Tony Skywalker
# @File    : download.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.requests.download_dto import DownloadFileContentSuccessData
from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.models import Item
from artifact.utils.file_util import refine_content
from live.models import ShareAuth
from shared.dtos.ordinary_response_dto import BadRequestDto, ForbiddenDto, NotFoundDto, InternalServerErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    InternalServerErrorResponse, OkResponse
from shared.utils.dir_utils import get_item_path
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import load_binary_file, construct_file_response, load_text_file
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['GET'])
@csrf_exempt
def download_file(request):
    user = get_user_from_request(request)
    params = parse_param(request)

    proj_id = parse_value(params.get('projId'), int)
    item_id = parse_value(params.get('itemId'), int)
    version = parse_value(params.get('version'), int)
    if proj_id is None or item_id is None:
        return BadRequestResponse(BadRequestDto("Missing parameters"))
    item: Item = first_or_default(Item, id=item_id)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != proj_id:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    if version is None or version == 0:
        version = item.version
    if version > item.total_version or version <= 0:
        return NotFoundResponse(NotFoundDto("Version does not exist"))

    path = get_item_path(item, version)
    filename = item.get_filename()

    try:
        response = construct_file_response(load_binary_file(path), filename)
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("File does not exist", data=e))

    return response


@api_view(['GET'])
@csrf_exempt
def download_file_content(request):
    user = get_user_from_request(request)
    params = parse_param(request)

    proj_id = parse_value(params.get('projId'), int)
    item_id = parse_value(params.get('itemId'), int)
    version = parse_value(params.get('version'), int)
    if proj_id is None or item_id is None:
        return BadRequestResponse(BadRequestDto("Missing parameters"))
    item: Item = first_or_default(Item, id=item_id)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != proj_id:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    if version is None or version == 0:
        version = item.version
    elif version > item.total_version or version < 0:
        return NotFoundResponse(NotFoundDto("Version does not exist"))

    path = get_item_path(item, version)
    filename = item.get_filename()

    try:
        with load_text_file(path) as file:
            content = file.read()
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("File does not exist", data=e))

    content = refine_content(item, content)

    return OkResponse(OkDto(data=DownloadFileContentSuccessData(ShareAuth.FULL, filename, content)))
