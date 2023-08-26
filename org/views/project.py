# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 23:13
# @Author  : Tony Skywalker
# @File    : project.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.models import Organization
from project.dtos.project_dto import ProjectDto
from project.models import Project
from shared.dtos.ordinary_response_dto import OkDto, BadRequestDto, UnauthorizedDto
from shared.response.json_response import OkResponse, NotFoundResponse, BadRequestResponse, UnauthorizedResponse
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['GET'])
@csrf_exempt
def get_projects_of_org(request):
    """
    Get all projects of an organization.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    org_id = parse_value(params.get('orgId'), int)
    if org_id is None:
        return BadRequestResponse(BadRequestDto("Missing orgId"))
    org, uop = get_org_with_user(org_id, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    org: Organization
    projects = Project.objects.filter(org_id=org.id)

    proj_list = []
    for project in projects:
        proj_list.append(ProjectDto(project))

    return OkResponse(OkDto({
        "projects": proj_list,
        "count": projects.count()
    }))
