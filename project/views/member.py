# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 20:31
# @Author  : Tony Skywalker
# @File    : member.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.models.upp_dto import UppDto
from project.dtos.requests.error_dtos import NoSuchProjectDto
from project.dtos.requests.update_upp_dto import UpdateUserProjectProfileDto
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.project_extension import get_project_with_user, get_upps_of_project
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
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
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto(request))

    params = parse_param(request)
    proj_id = parse_value(params.get("projId"), int)
    if proj_id is None:
        return BadRequestResponse(BadRequestDto("Missing projId"))
    proj, _ = get_project_with_user(proj_id, user)
    if proj is None:
        return NotFoundResponse(NoSuchProjectDto())

    member_list = []
    for upp in get_upps_of_project(proj):
        upp: UserProjectProfile
        user = upp.get_user()
        if user is None or not user.is_active():
            continue
        member_list.append(UppDto(user, upp))

    return OkResponse(OkDto(data={
        "members": member_list,
        "total": len(member_list)
    }))
