# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 21:10
# @Author  : Tony Skywalker
# @File    : creation.py
#
# Description:
#   Organization creation and deletion
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.cancel_org_dto import CancelOrgDto, CancelOrgSuccessData, CancelOrgErrorData
from org.dtos.register_org_dto import RegisterOrgDto
from org.models import Organization
from org.utils.cancel_org import cancel_organization
from org.utils.org_profile_provider import org_profile_provider_full
from shared.dtos.OrdinaryResponseDto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def create_org(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    param = parse_param(request)
    try:
        dto: RegisterOrgDto = deserialize(param, RegisterOrgDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto())
    org = Organization.create(0, dto.name, dto.description)
    org.save()

    uop = UserOrganizationProfile.create(UserAuth.CREATOR, user, org)
    uop.save()

    data = org_profile_provider_full(org)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def cancel_org(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: CancelOrgDto = deserialize(params, CancelOrgDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    data = CancelOrgSuccessData()
    data.errors.clear()
    for oid in dto.organizations:
        org, uop = get_org_with_user(oid, user)
        if org is None:
            data.errors.append(CancelOrgErrorData(oid, "No such organization"))
            continue
        uop: UserOrganizationProfile
        if uop.auth != UserAuth.CREATOR:
            data.errors.append(CancelOrgErrorData(oid, "Not creator"))
            continue
        cancel_organization(org)

    return OkResponse(OkDto(data=data))
