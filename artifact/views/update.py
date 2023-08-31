# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 22:38
# @Author  : Tony Skywalker
# @File    : update.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.dtos.models.item_dto import FolderDto, FileDto
from artifact.dtos.requests.request_dto import UpdateItemStatusDto, UpdateItemInfoDto
from artifact.models import Item
from artifact.utils.item_util import update_item_status_aux
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, NotFoundDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def update_item_name(request):
    """
    update info of item
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdateItemInfoDto = deserialize(params, UpdateItemInfoDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error:
        return NotFoundResponse(error)

    item: Item = first_or_default(Item, id=dto.itemId)
    if item is None:
        return NotFoundResponse(NotFoundDto("No such item"))
    if item.proj_id != dto.projId:
        return NotFoundResponse(NotFoundDto("Item is not under this project"))

    item.name = dto.filename
    item.save()

    return OkResponse(OkDto(data=FolderDto(item) if item.is_dir() else FileDto(item)))


@api_view(['POST'])
@csrf_exempt
def update_item_status(request):
    """
    update the status of an item, delete or recover.
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
