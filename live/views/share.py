# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 3:10
# @Author  : Tony Skywalker
# @File    : live.py
#
from datetime import timedelta

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.models import Item
from live.dto.authorize_dto import AuthorizeData
from live.dto.get_share_token_dto import GetShareTokenDto
from live.dto.share_token_dto import ShareTokenCompleteDto, ShareTokenDto
from live.models import ShareToken, ShareAuth
from live.utils.authorize import authorize_share_token_aux
from project.models import Project
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, NotFoundDto, OkDto, ForbiddenDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse, \
    ForbiddenResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.token.token import generate_basic_token


@api_view(['POST'])
@csrf_exempt
def create_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: GetShareTokenDto = deserialize(params, GetShareTokenDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto())
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    artifact: Item = first_or_default(Item, id=dto.itemId)
    if artifact is None:
        return NotFoundResponse(NotFoundDto())
    if not artifact.is_active():
        return ForbiddenResponse(ForbiddenDto("Artifact not active"))

    # only user in project can share the artifact
    proj, org, error = get_proj_and_org(artifact.proj_id, user)
    if error is not None:
        return NotFoundResponse(error)
    proj: Project
    if proj is None:
        return NotFoundResponse(NotFoundDto("No such project"))
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    # generate new share token
    token = generate_basic_token(31)
    created = timezone.now()
    expires = (created + timedelta(days=dto.expires)) if dto.expires > 0 else None
    share_token = ShareToken.create(artifact.id, proj.id, proj.org_id, token, created, expires, dto.auth, dto.orgOnly)
    share_token.save()

    return OkResponse(OkDto(data=ShareTokenCompleteDto(share_token)))


@api_view(['POST'])
@csrf_exempt
def revoke_share_token(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    share_token: ShareToken = first_or_default(ShareToken, token=token)
    if share_token is None:
        return NotFoundResponse(NotFoundDto(data=AuthorizeData(ShareAuth.DENIED, "Invalid token")))

    # only user in project can revoke share token
    proj, upp = get_project_with_user(share_token.proj_id, user)
    proj: Project
    if proj is None:
        return NotFoundResponse(NotFoundDto("No such project"))

    # now can revoke token
    if not share_token.is_active():
        return OkResponse(OkDto("Token already expired or revoked", data=ShareTokenDto(share_token)))
    share_token.revoked = timezone.now()
    share_token.save()

    return OkResponse(OkDto("Token revoked", data=ShareTokenDto(share_token)))


@api_view(['GET'])
@csrf_exempt
def authorize_share_token(request):
    params = parse_param(request)
    token = parse_value(params.get('token'), str)
    if token is None:
        return BadRequestResponse(BadRequestDto("Missing token"))

    user = get_user_from_request(request)
    data = authorize_share_token_aux(token, user)

    return OkResponse(OkDto(data=data))


@api_view(['GET'])
@csrf_exempt
def get_share_tokens_of_artifact(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    art_id = parse_value(params.get('artId'), int)
    if art_id is None:
        return BadRequestResponse(BadRequestDto("Missing artId"))

    artifact: Artifact = first_or_default(Artifact, id=art_id)
    if artifact is None:
        return NotFoundResponse(NotFoundDto())

    # only user in project can see share token
    proj, upp = get_project_with_user(artifact.proj_id, user)
    proj: Project
    if proj is None:
        return NotFoundResponse(NotFoundDto("No such project"))

    # get all tokens
    token_list = []
    for token in ShareToken.objects.filter(art_id=art_id):
        token_list.append(ShareTokenDto(token))

    return OkResponse(OkDto(data={
        "tokens": token_list,
        "total": len(token_list)
    }))
