# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 9:47
# @Author  : Tony Skywalker
# @File    : org_record.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto
from shared.response.json_response import UnauthorizedResponse, OkResponse, NotFoundResponse
from shared.utils.model.organization_extension import get_last_org_record, get_org_with_user, get_last_org_with_uop
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from user.dtos.org_record_dto import UserOrgRecordDto, UserOrgRecordCompleteDto
from user.models import UserOrganizationRecord


@api_view(['POST'])
@csrf_exempt
def update_last_organization(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    org_id = parse_value(params.get('orgId'), int, 0)
    if org_id != 0:
        org, uop = get_org_with_user(org_id, user)
        if org is None:
            return NotFoundResponse(NoSuchOrgDto())

    record: UserOrganizationRecord = get_last_org_record(user)
    record.org_id = org_id
    record.save()

    return OkResponse(OkDto(data=UserOrgRecordDto(record)))


@api_view(['GET'])
@csrf_exempt
def get_last_organization(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    record, org, uop = get_last_org_with_uop(user)
    return OkResponse(OkDto(data=UserOrgRecordCompleteDto(record, org, uop)))
