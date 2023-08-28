# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 16:05
# @Author  : Tony Skywalker
# @File    : notification.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from notif.dtos.notif_dto import NotifDto
from notif.dtos.notif_request_dto import GetNotifDto, EditNotifDto
from notif.models import Notification, NotifStatus
from org.dtos.requests.error_dtos import NoSuchOrgDto
from shared.dtos.OperationResponseData import OperationResponseData, OperationErrorData
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto, OkDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse, NotFoundResponse, OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def get_notif_in_org(request):
    """
    {
        orgId:
        status: 0 (only unread) | 1 (all)
    }
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    try:
        dto: GetNotifDto = deserialize(params, GetNotifDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Invalid value for pagination"))

    org, uop = get_org_with_user(dto.orgId, user)
    if org is None:
        return NotFoundResponse(NoSuchOrgDto())

    if dto.status == NotifStatus.UNREAD:
        notifs = Notification.objects.filter(user_id=user.id, org_id=dto.orgId, status=dto.status)
    else:
        notifs = Notification.objects.filter(user_id=user.id, org_id=dto.orgId, status__in=NotifStatus.valid())
    notifs.order_by('-timestamp')

    #
    # TODO: pagination
    #
    # paginator = Paginator(notifs, dto.ps)
    # page = paginator.get_page(dto.p)
    #
    # notif_list = []
    # for notif in page.object_list:
    #     notif_list.append(NotifDto(notif))
    #
    # data = {
    #     'ps': dto.ps,
    #     'p': dto.p,
    #     'total': page.count(),
    #     'next': paginator.num_pages > page.number,
    #     'notifications': notif_list
    # }
    #

    unread_count = 0
    notif_list = []
    for notif in notifs:
        if notif.status == NotifStatus.UNREAD:
            unread_count += 1
        notif_list.append(NotifDto(notif))

    return OkResponse(OkDto(data={
        "notifications": notif_list,
        "total": len(notif_list),
        "unread": unread_count
    }))


@api_view(['POST'])
@csrf_exempt
def edit_notif(request):
    """
    {
        status: 0 unread | 1 read | 2 deleted,
        notifications: [
            id, id, ...
        ]
    }
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: EditNotifDto = deserialize(params, EditNotifDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    data = OperationResponseData().init()
    for nid in dto.notifications:
        notif: Notification = first_or_default(Notification, id=nid, user_id=user.id)
        # can only change status of un-deleted notification
        if notif is None or notif.status == NotifStatus.DELETED:
            data.errors.append(OperationErrorData(nid, "No such notification"))
            continue
        notif.status = dto.status
        notif.save()
        data.success.append(nid)

    return OkResponse(OkDto(data=data))


# deprecated
@api_view(['POST'])
@csrf_exempt
def delete_notif(request):
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: EditNotifDto = deserialize(params, EditNotifDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    if not dto.is_valid():
        return BadRequestResponse(BadRequestDto("Bad value"))

    data = OperationResponseData().init()
    for nid in dto.notifications:
        notif: Notification = first_or_default(Notification, id=nid, user_id=user.id)
        if notif is None:
            data.errors.append(OperationErrorData(nid, "No such notification"))
            continue
        notif.delete()
        data.success.append(nid)

    return OkResponse(OkDto(data=data))
