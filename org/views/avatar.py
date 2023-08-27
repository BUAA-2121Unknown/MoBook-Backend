# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 19:57
# @Author  : Tony Skywalker
# @File    : avatar.py
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto, InternalServerErrorDto, BadRequestDto
from shared.response.json_response import UnauthorizedResponse, OkResponse, InternalServerErrorResponse, \
    BadRequestResponse, NotFoundResponse
from shared.utils.dir_utils import get_avatar_url, get_avatar_path
from shared.utils.file.avatar_util import save_avatar
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_image_name
from user.models import User, UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def upload_org_avatar(request):
    params = parse_param(request)

    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    oid = parse_value(params.get('orgId'), int)
    if oid is None:
        return BadRequestResponse(BadRequestDto("Missing orgId"))

    org, uop = get_org_with_user(oid, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop: UserOrganizationProfile
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Contact admin"))

    file = request.FILES.get('file')
    if file is None:
        return BadRequestResponse(BadRequestDto("Missing image file"))
    if not validate_image_name(file.name):
        return BadRequestResponse(BadRequestDto("Invalid image type!"))

    old_path = get_avatar_path('org', org.avatar)
    new_avatar = f"{org.id}.{file.name.split('.')[-1]}"
    new_path = get_avatar_path('org', new_avatar)

    # save image
    try:
        save_avatar('org', old_path, new_path, file)
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to save avatar", data=e))

    org.avatar = new_avatar
    org.save()

    return OkResponse(OkDto(data={"avatar": get_avatar_url('org', org.avatar)}))
