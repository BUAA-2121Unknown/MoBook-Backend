# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:39
# @Author  : Tony Skywalker
# @File    : profile.py

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.models import Item
from project.dtos.models.project_dto import ProjectCompleteDto
from project.dtos.requests.error_dtos import NoSuchProjectDto
from project.models import Project
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache, update_cached_object
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_proj_name, validate_proj_descr


@api_view(['POST'])
@csrf_exempt
def update_project_profile(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    _, proj = first_or_default_by_cache(Project, proj_id)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    name = parse_value(params.get('name'), str)
    if name is not None:
        if not validate_proj_name(name):
            return BadRequestResponse(BadRequestDto("Bad name"))
        proj.name = name
    descr = parse_value(params.get('description'), str)
    if descr is not None:
        if not validate_proj_descr(descr):
            return BadRequestResponse(BadRequestDto("Bad description"))
        proj.description = descr
    proj.save()

    update_cached_object(Project, proj.id, proj)

    root: Item = first_or_default(Item, id=proj.root_id)
    if root is not None:
        root.name = proj.name
        root.save()

    return OkResponse(OkDto(data={
        "name": proj.name,
        "description": proj.description
    }))


@api_view(['GET'])
@csrf_exempt
def get_project_profile(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return NotFoundResponse(error)
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    return OkResponse(OkDto(data=ProjectCompleteDto(proj)))
