# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 9:24
# @Author  : Tony Skywalker
# @File    : invitation.py
#
from datetime import timedelta

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.models.invitation_dto import InvitationDto
from org.dtos.models.user_org_profile_dto import UopDto
from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.dtos.requests.invitation_dtos import CreateInvitationDto, RevokeInvitationDto, ActivateInvSuccessData
from org.models import Invitation, Organization, PendingRecord
from org.utils.member import add_member_into_org
from shared.dtos.OrdinaryResponseDto import UnauthorizedDto, BadRequestDto, OkDto, NotFoundDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_with_user, get_org_profile_of_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.token.token import generate_basic_token
from user.models import UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def create_invitation(request):
    """
    Admin create a new invitation token.
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: CreateInvitationDto = deserialize(params, CreateInvitationDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    org, uop = get_org_with_user(dto.orgId, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop: UserOrganizationProfile
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Not admin"))

    token = generate_basic_token(31)
    created = timezone.now()
    expires = (created + timedelta(days=dto.expires)) if dto.expires > 0 else None
    invitation = Invitation.create(token, created, expires, dto.orgId, dto.review)
    invitation.save()

    return OkResponse(OkDto(data=InvitationDto(invitation)))


@api_view(['POST'])
@csrf_exempt
def revoke_invitation(request):
    """
    Admin revoke an old invitation
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: RevokeInvitationDto = deserialize(params, RevokeInvitationDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    org, uop = get_org_with_user(dto.orgId, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop: UserOrganizationProfile
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Not admin"))

    invitation: Invitation = first_or_default(Invitation, id=dto.id)
    if invitation is None:
        return NotFoundResponse(NotFoundDto("No such invitation"))
    if invitation.oid != dto.orgId:
        return UnauthorizedResponse(UnauthorizedDto("Not invitation of this org"))
    if not invitation.is_active():
        return OkResponse(OkDto("Already revoked or expired", data=InvitationDto(invitation)))
    invitation.revoked = timezone.now()
    invitation.save()
    
    return OkResponse(OkDto("Invitation revoked", data=InvitationDto(invitation)))


@api_view(['POST'])
@csrf_exempt
def activate_invitation(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    invitation: Invitation = first_or_default(Invitation, token=token)
    if invitation is None:
        return NotFoundResponse(NotFoundDto("No such invitation"))
    if not invitation.is_active():
        return UnauthorizedResponse(UnauthorizedDto("Invitation expired"))

    org = first_or_default(Organization, id=invitation.oid)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop = get_org_profile_of_user(org, user)
    if uop is not None:
        # previously in
        data = ActivateInvSuccessData(False, UopDto(user, uop), True)
        return OkResponse(OkDto(data=data))

    if invitation.review:
        PendingRecord.create(user.id, org.id).save()
        data = ActivateInvSuccessData(True, None, False)
    else:
        uop = add_member_into_org(org, user)
        data = ActivateInvSuccessData(False, UopDto(user, uop), False)

    return OkResponse(OkDto(data=data))
