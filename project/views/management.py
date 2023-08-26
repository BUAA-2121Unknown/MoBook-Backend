# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 21:47
# @Author  : Tony Skywalker
# @File    : management.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from project.dtos.create_project_dto import CreateProjectDto
from project.dtos.error_dtos import NoSuchProjectDto
from project.dtos.project_dto import ProjectCompleteDto
from project.dtos.update_project_status_dto import UpdateProjectStatusDto
from project.models import Project
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_with_user
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

    # TODO: import members

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

    proj = first_or_default(Project, id=dto.projId)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())

    proj.status = dto.status
    proj.save()

    return OkResponse(OkDto(data={"status": proj.status}))

# response = FileResponse(open(md_url, "rb"))
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(document.document_title + '.md'))
# return response
