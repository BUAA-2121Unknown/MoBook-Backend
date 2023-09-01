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
from artifact.dtos.requests.request_dto import DownloadFileDto
from artifact.models import Item
from artifact.utils.file_util import create_version_aux
from live.dtos.authorize_dto import AuthorizeData
from live.models import ShareAuth
from live.utils.authorize import authorize_share_token_aux
from live.utils.token_handler import parse_share_token
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, InternalServerErrorDto, \
    OkDto, NotFoundDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    InternalServerErrorResponse, OkResponse
from shared.utils.dir_utils import get_item_path
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import load_file, construct_file_response
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
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


@api_view(['GET'])
@csrf_exempt
def download_file(request):
    user = get_user_from_request(request)
    params = parse_param(request)

    proj_id = parse_value(params.get('projId'), int)
    item_id = parse_value(params.get('itemId'), int)
    token = parse_value(params.get('token'), str)
    version = parse_value(params.get('version'), int)
    if token is not None and len(token) > 0:
        item_id, proj_id = parse_share_token(token)
        if item_id is None or proj_id is None:
            return BadRequestResponse(BadRequestDto("Invalid token"))
    if proj_id is None or item_id is None:
        return BadRequestResponse(BadRequestDto("Missing parameters"))

    dto = DownloadFileDto().init(proj_id, item_id, token, version)
    if len(dto.token) > 0:
        auth_response = _authorize_with_token(dto, user)
    else:
        auth_response = _authorize_without_token(dto, user)
    if auth_response is not None:
        return auth_response

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != dto.projId:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Item is a directory"))

    if dto.version is None:
        dto.version = item.version
    if dto.version > item.total_version or dto.version <= 0:
        return NotFoundResponse(NotFoundDto("Version does not exist"))

    path = get_item_path(item, dto.version)

    try:
        with load_file(path) as file:
            filename = item.get_filename()
            response = construct_file_response(file, filename)
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("File does not exist", data=e))

    return response


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
