# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 20:35
# @Author  : Tony Skywalker
# @File    : profile.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.error_dtos import NoSuchOrgDto
from org.models import Organization
from org.utils.org_profile_provider import org_profile_provider_simple, org_profile_provider_full
from shared.dtos.OrdinaryResponseDto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_org_name, validate_org_descr
from user.models import UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def update_org_profile(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    oid = parse_value(params.get('id'), int)
    if oid is None:
        return BadRequestResponse(BadRequestDto("Missing id"))
    org, uop = get_org_with_user(oid, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop: UserOrganizationProfile
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Contact admin"))

    name = parse_value(params.get('name'), str)
    descr = parse_value(params.get("description"), str)
    org: Organization
    if name is not None:
        if not validate_org_name(name):
            return BadRequestResponse(BadRequestDto("Invalid name"))
        org.name = name
    if descr is not None:
        if not validate_org_descr(descr):
            return BadRequestResponse(BadRequestDto("Invalid description"))
        org.description = descr
    org.save()

    return OkResponse(OkDto({
        "name": org.name,
        "description": org.description
    }))


@api_view(['GET'])
@csrf_exempt
def get_org_profile(request):
    """
    Should log in, too
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    oid = parse_value(params.get('id'), int)
    if oid is None:
        return BadRequestResponse(BadRequestDto("Missing id"))
    org, uop = get_org_with_user(oid, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    if parse_value(params.get('mode'), str) == 'full':
        provider = org_profile_provider_full
    else:
        provider = org_profile_provider_simple
    data = provider(org)

    return OkResponse(OkDto(data=data))
