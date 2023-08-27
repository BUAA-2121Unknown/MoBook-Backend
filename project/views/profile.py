# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 22:39
# @Author  : Tony Skywalker
# @File    : profile.py

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.models.artifact_dto import ArtifactDto
from project.dtos.requests.error_dtos import NoSuchProjectDto
from project.models import Project, Artifact
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.model.model_extension import first_or_default, Existence
from shared.utils.model.project_extension import get_proj_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value, parse_value_with_check
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
    proj: Project = first_or_default(Project, id=proj_id)
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

    return OkResponse(OkDto({
        "name": proj.name,
        "description": proj.description
    }))


@api_view(['GET'])
@csrf_exempt
def get_artifacts_of_project(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    proj_id = parse_value(params.get('projId'), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))

    proj, upp = get_proj_with_user(proj_id, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    status = parse_value_with_check(params.get('status'), int, Existence.get_validator(), Existence.ACTIVE)
    artifacts = Artifact.objects.filter(proj_id=proj_id, status=status)

    art_list = []
    for art in artifacts:
        art_list.append(ArtifactDto(art))

    return OkResponse(OkDto({
        "artifacts": art_list,
        "total": len(artifacts)
    }))
