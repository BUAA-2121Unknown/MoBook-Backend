# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 10:45
# @Author  : Tony Skywalker
# @File    : pending.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.dtos.requests.pending_dto import UpdatePendingDto, UpdatePendingSuccessData
from org.models import PendingRecord, PendingStatus
from org.utils.member import add_user_into_org
from shared.dtos.OrdinaryResponseDto import UnauthorizedDto, BadRequestDto, NotFoundDto, ForbiddenDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def user_update_pending(request):
    """
    User side pending operations.
    revoke: if invitation require review, then user can revoke it before admin review
    delete: mark the invitation as deleted, just not display, **won't revoke yet**
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdatePendingDto = deserialize(params, UpdatePendingDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid() or dto.action not in PendingStatus.user():
        return BadRequestResponse(BadRequestDto("Bad value"))

    pending: PendingRecord = first_or_default(PendingRecord, id=dto.id)
    if pending is None:
        return NotFoundResponse(NotFoundDto("No such pending"))
    if not pending.editable():
        return ForbiddenResponse(ForbiddenDto("Not editable"))

    if dto.action == PendingStatus.REVOKED:
        pending.user_status = pending.admin_status = PendingStatus.REVOKED
    elif dto.action == PendingStatus.DELETED:
        if not pending.deletable():
            return ForbiddenResponse(ForbiddenDto("Not deletable"))
        pending.user_status = PendingStatus.DELETED

    pending.save()

    return OkResponse(OkDto(data=UpdatePendingSuccessData(pending)))


@api_view(['POST'])
@csrf_exempt
def admin_update_pending(request):
    """
    Admin side invitation operations.
    accept: accept user request
    reject: reject user request
    delete: delete pending record (soft)
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdatePendingDto = deserialize(params, UpdatePendingDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid() or dto.action not in PendingStatus.admin():
        return BadRequestResponse(BadRequestDto("Bad value"))

    pending: PendingRecord = first_or_default(PendingRecord, id=dto.id)
    if pending is None:
        return NotFoundResponse(NotFoundDto("No such pending"))
    if not pending.editable():
        return ForbiddenResponse(ForbiddenDto("Not editable"))

    org, uop = get_org_with_user(pending.oid, user)
    uop: UserOrganizationProfile
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Not admin"))

    # now is admin editing
    if dto.action == PendingStatus.ACCEPTED:
        pending.user_status = pending.admin_status = PendingStatus.ACCEPTED
        add_user_into_org(org, user)
        # TODO: send notification
    elif dto.action == PendingStatus.REJECTED:
        pending.user_status = pending.admin_status = PendingStatus.REJECTED
        # TODO: send notification of rejection
    elif dto.action == PendingStatus.DELETED:
        if not pending.deletable():
            return ForbiddenResponse(ForbiddenDto("Not deletable"))
        pending.admin_status = PendingStatus.DELETED
    pending.save()

    return OkResponse(OkDto(data=UpdatePendingSuccessData(pending)))
