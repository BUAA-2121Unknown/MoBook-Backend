# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 9:54
# @Author  : Tony Skywalker
# @File    : register.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from user.models import User
from oauth.dtos.activate_dto import ActivateDto
from oauth.dtos.register_dto import RegisterDto
from oauth.dtos.send_activation_dto import SendActivationDto
from oauth.tasks.send_email_task import send_activation_email_task
from shared.dtos.OrdinaryResponseDto import BadRequestDto, ForbiddenDto, OkDto, ErrorDto
from shared.response.json_response import BadRequestResponse, ForbiddenResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param
from shared.utils.token.password import generate_password
from shared.utils.validator import validate_email, validate_username, validate_password


@api_view(['POST'])
@csrf_exempt
def send_activation_link(request):
    params = parse_param(request)
    try:
        dto: SendActivationDto = deserialize(params, SendActivationDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    user: User = first_or_default(User, email=dto.email)
    if user is None:
        return OkResponse(ErrorDto(100010, "Invalid email"))
    if user.activated:
        return ForbiddenResponse(ForbiddenDto("User already activated"))

    send_activation_email_task.delay(dto.email, dto.url)

    return OkResponse(OkDto("Activation link sent"))


@api_view(['POST'])
@csrf_exempt
def register(request):
    params = parse_param(request)
    try:
        dto: RegisterDto = deserialize(params, RegisterDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    if not validate_username(dto.username):
        return OkResponse(ErrorDto(100001, "Invalid username"))
    if not validate_password(dto.password):
        return OkResponse(ErrorDto(100002, "Invalid password"))
    if not validate_email(dto.email):
        return OkResponse(ErrorDto(100003, "Invalid email"))

    user = first_or_default(User, username=dto.username)
    if user is not None:
        return OkResponse(ErrorDto(100004, "User already registered"))

    password = generate_password(dto.password)
    User.create(dto.username, password, dto.email).save()

    return OkResponse(OkDto("Welcome to MoBook, activate later~"))


@api_view(['POST'])
@csrf_exempt
def activate(request):
    params = parse_param(request)
    try:
        dto: ActivateDto = deserialize(params, ActivateDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    user: User = first_or_default(User, email=dto.email)
    if user is None:
        return OkResponse(ErrorDto(100005, "User not registered"))
    if user.activated:
        return OkResponse(OkDto("User already activated"))

    user.activated = True
    user.save()

    return OkResponse(OkDto("User successfully activated!"))
