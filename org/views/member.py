# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 21:45
# @Author  : Tony Skywalker
# @File    : member.py
#

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from org.dtos.models.user_org_profile_dto import UopDto
from org.dtos.requests.error_dtos import NoSuchOrgDto
from org.dtos.requests.kick_member_dto import KickMemberDto, KickMemberSuccessData, KickMemberErrorData
from org.dtos.requests.update_member_profile_dto import UpdateMemberProfileDto
from org.models import Organization
from org.utils.member import kick_member_from_org
from shared.dtos.OrdinaryResponseDto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, NotFoundResponse, BadRequestResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_profile_of_user, get_org_with_user
from shared.utils.model.user_extension import get_user_from_request, get_user_by_id
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from user.dtos.error_dtos import NoSuchUserDto, NoSuchMemberDto
from user.models import User, UserOrganizationProfile, UserAuth


@api_view(['POST'])
@csrf_exempt
def update_org_member_profile(request):
    """
    {
        orgId:
        userId:
        profile: {
            nickname:
        },
        auth:
    }
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: UpdateMemberProfileDto = deserialize(params, UpdateMemberProfileDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto())

    # get working organization
    org: Organization = first_or_default(Organization, id=dto.orgId)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    # current user auth
    uop: UserOrganizationProfile = get_org_profile_of_user(org, user)
    if uop is None:
        return UnauthorizedResponse(UnauthorizedDto("Not your organization"))

    if dto.userId == user.id:
        target = user
        target_uop = uop
    else:
        # modify other user
        if uop.auth not in UserAuth.authorized():
            return UnauthorizedResponse(UnauthorizedDto("Not admin"))

        # get target user
        target: User = first_or_default(User, id=dto.userId)
        if target is None:
            return NotFoundResponse(NoSuchUserDto())

        # target user auth
        target_uop: UserOrganizationProfile = get_org_profile_of_user(org, target)
        if target_uop is None:
            return NotFoundResponse(NoSuchMemberDto())

        # only creator can modify other admins
        if target_uop.auth in UserAuth.authorized() and uop.auth != UserAuth.CREATOR:
            return UnauthorizedResponse(UnauthorizedDto("Be the creator to edit admin"))

    target_uop.nickname = dto.profile.nickname
    # fix: creator cannot be changed
    if target_uop.auth != UserAuth.CREATOR:
        target_uop.auth = dto.auth
    elif dto.auth != UserAuth.CREATOR:
        return BadRequestResponse(BadRequestDto("Cannot change creator"))

    target_uop.save()

    return OkResponse(OkDto(data=UopDto(target, target_uop)))


@api_view(['GET'])
@csrf_exempt
def get_org_members_profile(request):
    """
    Get all member profiles in an org.
    ?orgId=123
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    org_id = parse_value(params.get('orgId'), int)
    if org_id is None:
        return BadRequestResponse(BadRequestDto("Missing orgId"))

    org, uop = get_org_with_user(org_id, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    data = {
        "orgId": org_id,
        "members": []
    }
    uops = UserOrganizationProfile.objects.filter(org_id=org_id)
    for uop in uops:
        user = get_user_by_id(uop.user_id)
        if user is None:
            continue
        data["members"].append(UopDto(user, uop))

    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def kick_member(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse
    params = parse_param(request)
    try:
        dto: KickMemberDto = deserialize(params, KickMemberDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    org, uop = get_org_with_user(dto.orgId, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())
    uop: UserOrganizationProfile
    if uop.auth not in UserAuth.authorized():
        return UnauthorizedResponse(UnauthorizedDto("Not admin"))

    data = KickMemberSuccessData()
    data.init()
    for uid in dto.members:
        if uid == user.id:
            data.errors.append(KickMemberErrorData(uid, "Cannot kick self"))
            continue
        target = get_user_by_id(uid)
        if target is None:
            data.errors.append(KickMemberErrorData(uid, "No such users"))
            continue
        target_org, target_uop = get_org_with_user(dto.orgId, target)
        target_uop: UserOrganizationProfile
        if target_org is None:
            data.errors.append(KickMemberErrorData(uid, "User not in org"))
            continue
        if target_uop in UserAuth.authorized() and uop.auth != UserAuth.CREATOR:
            data.errors.append(KickMemberErrorData(uid, "Not creator"))
            continue
        kick_member_from_org(target_org, target, target_uop)
        data.success.append(uid)

    return OkResponse(OkDto(data=data))
