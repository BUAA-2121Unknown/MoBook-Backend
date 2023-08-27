# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 12:08
# @Author  : Tony Skywalker
# @File    : attachment.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.models.artifact_dto import ArtifactDto
from project.dtos.requests.error_dtos import NoSuchProjectDto, NoSuchArtifactDto
from project.models import Artifact
from shared.dtos.ordinary_response_dto import OkDto, ForbiddenDto, UnauthorizedDto, BadRequestDto, \
    InternalServerErrorDto, NotFoundDto
from shared.response.json_response import OkResponse, ForbiddenResponse, NotFoundResponse, UnauthorizedResponse, \
    BadRequestResponse, InternalServerErrorResponse
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import parse_filename, save_file, construct_file_response, load_file
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_project_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value


@api_view(['POST'])
@csrf_exempt
def upload_artifact_attachment(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    art_id = parse_value(params.get('artId'), int)
    if art_id is None:
        return BadRequestResponse(BadRequestDto("Missing artId"))
    artifact: Artifact = first_or_default(Artifact, id=art_id)
    if artifact is None:
        return NotFoundResponse(NoSuchArtifactDto())

    # validate permissions
    proj, upp = get_project_with_user(artifact.proj_id, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))
    if not artifact.is_active():
        return ForbiddenResponse(ForbiddenDto("Artifact not active"))

    # get file
    file = request.FILES.get('file')
    if file is None:
        return BadRequestResponse(BadRequestDto("Missing attachment"))

    old_path = artifact.get_path()
    name, ext = parse_filename(file.name)
    artifact.filename = name
    artifact.extension = ext
    new_path = artifact.get_path()

    try:
        save_file(old_path, new_path, file)
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto(data=e))

    artifact.save()

    return OkResponse(OkDto(data=ArtifactDto(artifact)))


@api_view(['GET'])
@csrf_exempt
def download_artifact_attachment(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    art_id = parse_value(params.get('artId'), int)
    if art_id is None:
        return BadRequestResponse(BadRequestDto("Missing artId"))
    artifact: Artifact = first_or_default(Artifact, id=art_id)
    if artifact is None:
        return NotFoundResponse(NoSuchArtifactDto())

    # validate permissions
    proj, upp = get_project_with_user(artifact.proj_id, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))
    if not artifact.is_active():
        return ForbiddenResponse(ForbiddenDto("Artifact not active"))

    # get file
    if not artifact.has_file():
        return NotFoundResponse(NotFoundDto("No attachment"))

    try:
        filename = artifact.get_filename()
        filepath = artifact.get_path()
        if filename is None or filepath is None:
            raise FileException("File properties missing")
        file = load_file(filepath)
    except FileException as e:
        return NotFoundResponse(NotFoundDto(data=e))
    return construct_file_response(file, filename)
