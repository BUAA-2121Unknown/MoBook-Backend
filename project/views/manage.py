# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 21:47
# @Author  : Tony Skywalker
# @File    : management.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.utils.item_util import init_root_folder
from notif.dtos.notif_payload import NotifNewProjectPayload
from notif.utils.notif_manager import dispatch_notification
from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.models import Organization
from project.dtos.models.project_dto import ProjectCompleteDto
from project.dtos.requests.create_project_dto import CreateProjectDto
from project.dtos.requests.update_project_status_dto import UpdateProjectStatusDto
from project.models import Project
from shared.dtos.OperationResponseData import OperationResponseData, OperationErrorData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.organization_extension import get_org_with_user, get_users_of_org
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User


@api_view(['POST'])
@csrf_exempt
def create_project(request):
    """
    {
        orgId: 1,
        name: "bbb",
        description: "bbb"
    }
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: CreateProjectDto = deserialize(params, CreateProjectDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    org, uop = get_org_with_user(dto.orgId, user)
    org: Organization
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    if not org.is_active():
        return ForbiddenResponse(ForbiddenDto("Organization not active"))

    proj = Project.create(org.id, dto.name, dto.description)
    proj.save()

    # create root folder
    init_root_folder(proj)

    target_users = get_users_of_org(org)
    # send notifications
    for u in target_users:
        u: User
        if u.id == user.id:
            continue
        dispatch_notification(u.id, org.id, NotifNewProjectPayload(org, user, proj))

    return OkResponse(OkDto(data=ProjectCompleteDto(proj)))


@api_view(['POST'])
@csrf_exempt
def update_project_status(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: UpdateProjectStatusDto = deserialize(params, UpdateProjectStatusDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    data = OperationResponseData().init()
    for proj_id in dto.projects:
        proj, org, error = get_proj_and_org(proj_id, user)
        if error is not None:
            data.errors.append(OperationErrorData(proj_id, error))
            continue
        proj.status = dto.status
        proj.save()
        data.success.append(proj_id)

    return OkResponse(OkDto(data=data))
