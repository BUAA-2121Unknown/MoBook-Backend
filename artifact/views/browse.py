# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 20:20
# @Author  : Tony Skywalker
# @File    : browse.py
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.models.item_dto import FolderDto, FileCompleteDto
from artifact.dtos.models.version_dto import VersionDto
from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.dtos.requests.request_dto import GetVersionsDto, GetItemDto
from artifact.models import Item
from artifact.utils.version_util import get_versions_of_file
from project.models import Project
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['GET'])
@csrf_exempt
def get_items_of_project(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)
    proj: Project
    root: Item = first_or_default(Item, id=proj.root_id)
    if root is None or not root.is_active():
        return NotFoundResponse(NoSuchItemDto())

    data = Item.dump_bulk(root)
    return OkResponse(OkDto(data=data))


@api_view(['GET'])
@csrf_exempt
def get_item(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: GetItemDto = deserialize(params, GetItemDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)
    proj: Project

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())

    if item.is_dir():
        data = FolderDto(item)
    else:
        data = FileCompleteDto(item)

    return OkResponse(OkDto(data=data))


@api_view(['GET'])
@csrf_exempt
def get_all_versions(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: GetVersionsDto = deserialize(params, GetVersionsDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    # get working project
    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    # get file
    file: Item = first_or_default(Item, id=dto.itemId)
    if file is None or not file.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if file.is_dir():
        return ForbiddenResponse(ForbiddenDto("Not a file"))

    version_list = []
    for version in get_versions_of_file(file):
        version_list.append(VersionDto(version))

    return OkResponse(OkDto(data={
        "versions": version_list,
        "total": len(version_list)
    }))
