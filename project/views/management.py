# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 21:47
# @Author  : Tony Skywalker
# @File    : management.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from project.dtos.models.project_dto import ProjectCompleteDto
from project.dtos.requests.create_project_dto import CreateProjectDto
from project.dtos.requests.update_project_status_dto import UpdateProjectStatusDto
from project.models import Project
from project.utils.assistance import init_project_by_organization
from shared.dtos.OperationResponseData import OperationResponseData, OperationErrorData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.project_extension import get_proj_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param


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
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    proj = Project.create(org, dto.name, dto.description)
    proj.save()

    init_project_by_organization(proj)

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
        proj, upp = get_proj_with_user(proj_id, user)
        if proj is None:
            data.errors.append(OperationErrorData(proj_id, "No such project"))
            continue
        proj.status = dto.status
        proj.save()
        data.success.append(proj_id)

    return OkResponse(OkDto(data=data))
