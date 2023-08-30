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
from artifact.dtos.requests.request_dto import UploadFileDto, DownloadFileDto
from artifact.models import Item
from artifact.utils.file_util import create_version_aux
from live.dto.authorize_dto import AuthorizeData
from live.models import ShareAuth
from live.utils.authorize import authorize_share_token_aux
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, InternalServerErrorDto, \
    OkDto, NotFoundDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    InternalServerErrorResponse, OkResponse
from shared.utils.dir_utils import get_item_path
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import load_file, construct_file_response
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User


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
        version = create_version_aux(file, dto.version, item, user)
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to upload file", data=e))

    return OkResponse(OkDto(data=FileDto(item)))


@api_view(['GET'])
@csrf_exempt
def download_file(request):
    user = get_user_from_request(request)
    params = parse_param(request)

    try:
        dto: DownloadFileDto = deserialize(params, DownloadFileDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if len(dto.token) == 0:
        response = _authorize_with_token(dto, user)
    else:
        response = _authorize_without_token(dto, user)
    if response is not None:
        return response

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != dto.projId:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    if dto.version > item.version:
        return NotFoundResponse(NotFoundDto("Version does not exist"))

    path = get_item_path(item, dto.version)
    try:
        file = load_file(path)
        filename = item.get_filename()
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("File does not exist"))

    return construct_file_response(file, filename)


def _authorize_with_token(dto: DownloadFileDto, user: User):
    data: AuthorizeData = authorize_share_token_aux(dto.token, user)
    if data.auth != ShareAuth.FULL:
        return UnauthorizedResponse(UnauthorizedDto("Permission denied"))
    return None


def _authorize_without_token(dto: DownloadFileDto, user: User):
    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return UnauthorizedResponse(error)
    return None
