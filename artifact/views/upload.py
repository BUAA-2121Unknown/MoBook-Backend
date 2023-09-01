# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 9:20
# @Author  : Tony Skywalker
# @File    : upload.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.models.item_dto import FileDto
from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.dtos.requests.request_dto import UploadFileDto
from artifact.models import Item
from artifact.utils.file_util import create_version_aux, create_version_by_content_aux
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, InternalServerErrorDto, \
    OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    InternalServerErrorResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['POST'])
@csrf_exempt
def upload_file(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    file = request.FILES.get('file')
    if file is None:
        return BadRequestResponse(BadRequestDto("Missing file"))
    proj_id = parse_value(params.get('projId'), int)
    item_id = parse_value(params.get('itemId'), int)
    # filename = parse_value(params.get('filename'), str)
    version = parse_value(params.get('version'), int)
    if proj_id is None or item_id is None:
        return BadRequestResponse(BadRequestDto("Missing parameters"))
    if version is None or version == 0:
        # assign a large number, which will be adjusted automatically on save
        version = 2147483647
    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)

    item: Item = first_or_default(Item, id=item_id)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != proj_id:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    try:
        _ = create_version_aux(file, version, item, user)
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to upload file", data=e))

    return OkResponse(OkDto(data=FileDto(item)))


@api_view(['POST'])
@csrf_exempt
def upload_file_content(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UploadFileDto = deserialize(params, UploadFileDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != dto.projId:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    try:
        _ = create_version_by_content_aux(dto.content, dto.version, item, user)
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to upload file", data=e))

    return OkResponse(OkDto(data=FileDto(item)))
