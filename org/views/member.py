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
from org.dtos.requests.kick_member_dto import KickMemberDto, KickMemberErrorData
from org.models import Organization
from org.utils.assistance import kick_member_from_org
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, NotFoundResponse, BadRequestResponse, OkResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.organization_extension import get_org_profile_of_user, get_org_with_user, get_uops_of_org
from shared.utils.model.user_extension import get_user_from_request, get_user_by_id
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.validator import validate_member_nickname
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
    org_id = parse_value(params.get('orgId'), int)
    if org_id is None:
        return BadRequestResponse(BadRequestDto("Missing orgId"))
    user_id = parse_value(params.get('userId'), int)
    if user_id is None:
        return BadRequestResponse(BadRequestDto("Missing userId"))

    # get working organization
    _, org = first_or_default_by_cache(Organization, org_id)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    # current user auth
    uop: UserOrganizationProfile = get_org_profile_of_user(org, user)
    if uop is None:
        return UnauthorizedResponse(UnauthorizedDto("Not your organization"))

    profile = params.get('profile', None)
    nickname = None
    if profile is not None:
        nickname = parse_value(profile.get('nickname'), str)
        if nickname is not None and not validate_member_nickname(nickname):
            return BadRequestResponse(BadRequestDto("Invalid nickname"))
    auth = parse_value(params.get('auth'), int)

    if user_id == user.id:
        target = user
        target_uop = uop
    else:
        # modify other user
        if uop.auth not in UserAuth.authorized():
            return UnauthorizedResponse(UnauthorizedDto("Not admin"))

        # get target user
        _, target = first_or_default_by_cache(User, user_id)
        if target is None:
            return NotFoundResponse(NoSuchUserDto())

        # target user auth
        target_uop: UserOrganizationProfile = get_org_profile_of_user(org, target)
        if target_uop is None:
            return NotFoundResponse(NoSuchMemberDto())

        # only creator can modify other admins
        if target_uop.auth in UserAuth.authorized() and uop.auth != UserAuth.CREATOR:
            return UnauthorizedResponse(UnauthorizedDto("Be the creator to edit admin"))

    if nickname is not None:
        target_uop.nickname = nickname

    # fix: creator cannot be changed
    if auth is not None:
        if target_uop.auth != UserAuth.CREATOR:
            target_uop.auth = auth
        elif auth != UserAuth.CREATOR:
            return BadRequestResponse(BadRequestDto("Cannot change creator"))

    target_uop.save()

    return OkResponse(OkDto(data=UopDto(target, target_uop)))


@api_view(['GET'])
@csrf_exempt
def get_members_of_org(request):
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

    org, _ = get_org_with_user(org_id, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    member_list = []
    for uop in get_uops_of_org(org):
        uop: UserOrganizationProfile
        user: User = uop.get_user()
        if user is None or not user.is_active():
            continue
        member_list.append(UopDto(user, uop))

    return OkResponse(OkDto(data={
        "members": member_list,
        "total": len(member_list)
    }))


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

    data = OperationResponseData().init()
    for uid in dto.users:
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
