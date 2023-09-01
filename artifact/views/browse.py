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
from artifact.models import Item
from artifact.utils.item_filter import filter_active_items, filter_recycled_items
from artifact.utils.version_util import get_versions_of_file
from project.models import Project
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse
from shared.utils.model.model_extension import first_or_default, Existence
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value, parse_value_with_check


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
    status = parse_value_with_check(params.get('status'), int, Existence.get_validator())
    if status is None:
        return BadRequestResponse(BadRequestDto("status missing or invalid"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)
    proj: Project
    root: Item = first_or_default(Item, id=proj.root_id)
    if root is None or not root.is_active():
        return NotFoundResponse(NoSuchItemDto())

    raw_data = Item.dump_bulk(root)

    if status == Existence.ACTIVE:
        data = filter_active_items(raw_data)
        if len(data) == 0:
            data = None
        else:
            data = data[0]
    else:
        data = filter_recycled_items(raw_data)

    return OkResponse(OkDto(data=data))


@api_view(['GET'])
@csrf_exempt
def get_item(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    item_id = parse_value(params.get('itemId'), int)
    if item_id is None:
        return BadRequestResponse(BadRequestDto("Missing itemId"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)
    proj: Project

    item: Item = first_or_default(Item, id=item_id)
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
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    item_id = parse_value(params.get('itemId'), int)
    if item_id is None:
        return BadRequestResponse(BadRequestDto("Missing itemId"))

    # get working project
    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)

    # get file
    file: Item = first_or_default(Item, id=item_id)
    if file is None or not file.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if file.is_dir():
        return ForbiddenResponse(ForbiddenDto("Not a file"))

    version_list = []
    for version in get_versions_of_file(file):
        version_list.append(VersionDto(version))

    return OkResponse(OkDto(data={
        "itemId": item_id,
        "lastVersion": file.version,
        "versions": version_list,
        "total": len(version_list)
    }))


@api_view
@csrf_exempt
def get_prototypes_of_project(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    status = parse_value_with_check(params.get('status'), int, Existence.get_validator())
    if status is None:
        return BadRequestResponse(BadRequestDto("status missing or invalid"))

    proj, org, error = get_proj_and_org(proj_id, user)
    if error:
        return NotFoundResponse(error)
    proj: Project
    root: Item = first_or_default(Item, id=proj.root_id)
    if root is None or not root.is_active():
        return NotFoundResponse(NoSuchItemDto())

    raw_data = Item.dump_bulk(root)

    if status == Existence.ACTIVE:
        data = filter_active_items(raw_data)
        if len(data) == 0:
            data = None
        else:
            data = data[0]
    else:
        data = filter_recycled_items(raw_data)

    return OkResponse(OkDto(data=data))