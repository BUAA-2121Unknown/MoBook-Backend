# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/29/2023 16:56
# @Author  : Tony Skywalker
# @File    : manage.py
#
# Description:
#   Basic management of items. Creation depends on artifact implementation.
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.dtos.models.item_dto import FolderDto, FileDto
from artifact.dtos.requests.request_dto import CreateFolderDto, CreateFileDto, UpdateItemStatusDto, MoveItemDto
from artifact.models import Item
from artifact.utils.item_util import create_folder_aux, create_file_aux, update_item_status_aux, move_item_aux
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse
from shared.utils.file.exceptions import FileException
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def create_folder(request):
    """
    Create a new folder under one folder.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: CreateFolderDto = deserialize(params, CreateFolderDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != dto.projId:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if not item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Not a folder"))

    folder = create_folder_aux(item, dto.name, proj)

    return OkResponse(OkDto(data=FolderDto(folder)))


@api_view(['POST'])
@csrf_exempt
def create_file(request):
    """
    Create a new file under one folder.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: CreateFileDto = deserialize(params, CreateFileDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None or not item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if item.proj_id != dto.projId:
        return BadRequestResponse(BadRequestDto("Item is not under this project"))
    if not item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Not a folder"))

    try:
        file, version = create_file_aux(item, dto.filename, dto.prop, dto.live, None, user, proj)
    except FileException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    return OkResponse(OkDto(data=FileDto(file)))


@api_view(['POST'])
@csrf_exempt
def update_item_status(request):
    """
    Update the status of an item, delete or recover.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdateItemStatusDto = deserialize(params, UpdateItemStatusDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    data = OperationResponseData().init()
    for item_id in list(set(dto.items)):
        item: Item = first_or_default(Item, id=item_id)
        if item is None:
            data.add_error(item_id, "No such item")
            continue
        if item.proj_id != dto.projId:
            data.add_error(item_id, "Item is not under this project")
            continue
        update_item_status_aux(item, dto.status)
        data.add_success(item_id)

    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def move_item(request):
    """
    Move an item to another folder.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: MoveItemDto = deserialize(params, MoveItemDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    # get working project
    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    # check dst item
    dst_item: Item = first_or_default(Item, id=dto.folderId)
    if dst_item is None or not dst_item.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if not dst_item.is_dir():
        return ForbiddenResponse(ForbiddenDto("Not a folder"))

    # move items
    data = OperationResponseData().init()
    for item_id in list(set(dto.items)):
        item: Item = first_or_default(Item, id=item_id)
        try:
            move_item_aux(item, dst_item)
            data.add_success(item_id)
        except Exception as e:
            data.add_error(item_id, str(e))

    return OkResponse(OkDto(data=data))
