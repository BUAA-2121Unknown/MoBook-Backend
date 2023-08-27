# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 20:31
# @Author  : Tony Skywalker
# @File    : member.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.requests.error_dtos import NoSuchProjectDto
from project.dtos.requests.update_upp_dto import UpdateUserProjectProfileDto
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.project_extension import get_project_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import UserProjectProfile


@api_view(['POST'])
@csrf_exempt
def update_project_member_profile(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto(request))

    params = parse_param(request)
    try:
        dto: UpdateUserProjectProfileDto = deserialize(params, UpdateUserProjectProfileDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    if dto.userId != user.id:
        return UnauthorizedResponse(UnauthorizedDto("Can only change your profile"))

    proj, upp = get_project_with_user(dto.projId, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())
    upp: UserProjectProfile
    upp.role = dto.role
    upp.save()

    return OkResponse(OkDto(data={
        "role": upp.role
    }))


@api_view(['GET'])
@csrf_exempt
def get_project_members(request):
    pass
