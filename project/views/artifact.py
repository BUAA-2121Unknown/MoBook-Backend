# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/27/2023 9:30
# @Author  : Tony Skywalker
# @File    : project.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.models.artifact_dto import ArtifactCompleteDto
from project.dtos.requests.create_artifact_dto import CreateArtifactDto
from project.dtos.requests.error_dtos import NoSuchProjectDto, NoSuchArtifactDto
from project.dtos.requests.update_artifact_status_dto import UpdateArtifactStatusDto
from project.models import Artifact, Project
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_artifact_name, validate_artifact_type


@api_view(['POST'])
@csrf_exempt
def create_artifact(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: CreateArtifactDto = deserialize(params, CreateArtifactDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    proj, upp = get_proj_with_user(dto.projId, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    artifact = Artifact.create(proj, dto.type, dto.name, dto.live)
    artifact.save()

    return OkResponse(OkDto(data=ArtifactCompleteDto(artifact)))


@api_view(['POST'])
@csrf_exempt
def update_artifact(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    art_id = parse_value(params.get('artId'), int)
    if art_id is None:
        return BadRequestResponse(BadRequestDto("Missing artId"))
    art: Artifact = first_or_default(Artifact, id=art_id)
    if art is None:
        return NotFoundResponse(NoSuchArtifactDto())

    # check belonging
    proj, upp = get_proj_with_user(art.proj_id, user)
    proj: Project
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    # check artifact status
    if not art.is_active():
        return ForbiddenResponse(ForbiddenDto("Artifact not active"))

    name = parse_value(params.get('name'), str)
    if name is not None:
        if not validate_artifact_name(name):
            return BadRequestResponse(BadRequestDto("Bad name"))
        art.name = name
    typ = parse_value(params.get('type'), str)
    if typ is not None:
        if not validate_artifact_type(typ):
            return BadRequestResponse(BadRequestDto("Bad type"))
        art.type = typ
    art.save()

    return OkResponse(OkDto(data={
        "name": art.name,
        "type": art.type
    }))


@api_view(['POST'])
@csrf_exempt
def update_artifact_status(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdateArtifactStatusDto = deserialize(params, UpdateArtifactStatusDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    data = OperationResponseData().init()
    for art_id in dto.artifacts:
        art: Artifact = first_or_default(Artifact, id=art_id)
        if art is None:
            data.add_error(art_id, "No such artifact")
            continue
        # check belonging
        proj, upp = get_proj_with_user(art.proj_id, user)
        proj: Project
        if proj is None:
            data.add_error(art_id, "Belonging project not exists")
            continue
        if not proj.is_active():
            data.add_error(art_id, "Belonging project not active")
            continue
        art.status = dto.status
        art.save()
        data.add_success(art_id)

    return OkResponse(OkDto(data=data))
