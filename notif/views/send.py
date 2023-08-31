# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 10:29
# @Author  : Tony Skywalker
# @File    : send.py
#
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from artifact.models import Item
from notif.dtos.notif_payload import NotifFileAtPayload
from notif.dtos.send_art_at_dto import SendFileAtNotif
from notif.utils.notif_manager import dispatch_notification
from project.models import Project
from shared.dtos.OperationResponseData import OperationResponseData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, NotFoundDto, ForbiddenDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, ForbiddenResponse, \
    OkResponse
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_profile_of_user
from shared.utils.model.project_extension import get_proj_and_org
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User


@api_view(['POST'])
@csrf_exempt
def send_file_at_notif(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: SendFileAtNotif = deserialize(params, SendFileAtNotif)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))

    proj, org, error = get_proj_and_org(dto.projId, user)
    if error is not None:
        return NotFoundResponse(error)
    proj: Project
    if not proj.is_active():
        return ForbiddenResponse(ForbiddenDto("Project not active"))

    file: Item = first_or_default(Item, id=dto.fileId)
    if file is None:
        return NotFoundResponse(NotFoundDto("No such file"))
    if not file.is_active():
        return ForbiddenResponse(ForbiddenDto("File not active"))

    if file.proj_id != proj.id:
        return BadRequestResponse(BadRequestDto("File belongs to different project"))

    org = proj.get_org()
    if org is None or not org.is_active():
        return NotFoundResponse(NotFoundDto("No such organization"))

    data = OperationResponseData().init()
    # remove duplication
    for uid in list(set(dto.users)):
        target = first_or_default_by_cache(User, uid)
        if target is None:
            data.add_error(uid, "No such user")
            continue
        if get_org_profile_of_user(org, target) is None:
            data.add_error(uid, "User not in organization")
            continue
        if uid == user.id:
            data.add_error(uid, "Cannot send notification to yourself")
            continue
        dispatch_notification(uid, org.id, NotifFileAtPayload(org, user, proj, file))
        data.add_success(uid)

    return OkResponse(OkDto(data=data))
