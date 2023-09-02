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

from artifact.dtos.models.item_dto import FolderDto, FileDto
from artifact.dtos.requests.error_dtos import NoSuchItemDto
from artifact.dtos.requests.request_dto import CreateFolderDto, CreateFileDto, MoveItemDto, \
    DuplicateItemDto, DeleteItemDto
from artifact.models import Item, ItemType
from artifact.utils.delete import delete_item_aux
from artifact.utils.duplicate import duplicate_item_aux
from artifact.utils.item_util import create_folder_aux, move_item_aux, create_file_by_content_aux
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, ForbiddenDto, OkDto, \
    InternalServerErrorDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse, InternalServerErrorResponse
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

    folder = create_folder_aux(item, dto.filename, proj, user)

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
    if dto.sibling:
        if item.is_root():
            return ForbiddenResponse(ForbiddenDto("Can't create sibling file under root folder"))
        item = item.get_parent()

    try:
        file, version = create_file_by_content_aux(item, dto.filename, dto.prop, dto.live, dto.content, user, proj)
    except FileException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    return OkResponse(OkDto(data=FileDto(file)))


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


@api_view(['POST'])
@csrf_exempt
def duplicate_item(request):
    """
    Move an item to another folder.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: DuplicateItemDto = deserialize(params, DuplicateItemDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    # get working project
    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    # check template
    template: Item = first_or_default(Item, id=dto.itemId)
    if template is None or not template.is_active():
        return NotFoundResponse(NoSuchItemDto())
    if template.type == ItemType.ROOT:
        return ForbiddenResponse(ForbiddenDto("Cannot duplicate root folder"))

    # duplicate item
    parent = template.get_parent()
    new_item: Item = duplicate_item_aux(parent, template)
    if new_item is None:
        return InternalServerErrorResponse(InternalServerErrorDto("Field to duplicate item"))
    new_item.name = template.name + " (Copy)"
    new_item.save()

    return OkResponse(OkDto(data=FolderDto(new_item) if new_item.is_dir() else FileDto(new_item)))


@api_view(['POST'])
@csrf_exempt
def delete_item(request):
    """
    Move an item to another folder.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: DeleteItemDto = deserialize(params, DeleteItemDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

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
        if item.type == ItemType.ROOT:
            data.add_error(item_id, "Cannot delete root folder")
            continue
        delete_item_aux(item)
        data.add_success(item_id)

    return OkResponse(OkDto(data=data))
