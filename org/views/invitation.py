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

from org.dtos.models.invitation_dto import InvitationDto, InvitationCompleteDto
from org.dtos.models.user_org_profile_dto import UopDto
from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.dtos.requests.invitation_dtos import CreateInvitationDto, RevokeInvitationDto, ActivateInvSuccessData
from org.models import Invitation, Organization, PendingRecord
from org.utils.assistance import add_member_into_org
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto, NotFoundDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.cache.cache_utils import update_cached_object, first_or_default_by_cache
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

    _, invitation = first_or_default_by_cache(Invitation, dto.id)
    if invitation is None:
        return NotFoundResponse(NotFoundDto("No such invitation"))
    if invitation.oid != dto.orgId:
        return UnauthorizedResponse(UnauthorizedDto("Not invitation of this org"))
    if not invitation.is_active():
        return OkResponse(OkDto("Already revoked or expired", data=InvitationDto(invitation)))
    invitation.revoked = timezone.now()
    invitation.save()

    update_cached_object(Invitation, invitation.id, invitation)

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

    _, org = first_or_default_by_cache(Organization, invitation.oid)
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


@api_view(['GET'])
@csrf_exempt
def get_invitation_of_org(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    org_id = parse_value(params.get('orgId'), int)
    if org_id is None:
        return BadRequestResponse(BadRequestDto("Missing orgId"))

    org, uop = get_org_with_user(org_id, user)
    org: Organization
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    if not org.is_active():
        return ForbiddenResponse(ForbiddenDto("Organization not active"))
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Not admin"))

    inv_list = []
    for inv in Invitation.objects.filter(oid=org_id):
        inv_list.append(InvitationDto(inv))

    return OkResponse(OkDto(data={
        "invitations": inv_list,
        "total": len(inv_list)
    }))


@api_view(['GET'])
@csrf_exempt
def get_preview_of_invitation(request):
    # need no authorization

    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))
    invitation: Invitation = first_or_default(Invitation, token=token)
    if invitation is None:
        return NotFoundResponse(NotFoundDto("No such invitation"))
    if not invitation.is_active():
        return UnauthorizedResponse(UnauthorizedDto("Invitation expired"))

    return OkResponse(OkDto(data=InvitationCompleteDto(invitation)))
