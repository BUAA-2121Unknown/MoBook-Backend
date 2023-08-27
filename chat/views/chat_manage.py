from django.shortcuts import render

import user
from chat.models import Chat
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto
from shared.response.json_response import UnauthorizedResponse, OkResponse
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User, UserChatRelation


def create_chat(request):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    # 建群
    type = params.get('type')
    org_id = params.get('org_id')
    chat_name = params.get('chat_name')

    chat = Chat(org_id=org_id, type=type, chat_name=chat_name)
    chat.save()

    # 拉创始人
    user_chat_relation = UserChatRelation(user_id=src.id, chat_id=chat.id, authority=1)
    user_chat_relation.save()

    # 拉n人
    invite_list = params.get('invite_list')
    for user_id in invite_list:
        user_chat_relation = UserChatRelation(user_id=user_id, chat_id=chat.id)
        user_chat_relation.save()

    return OkResponse(OkDto())


def dismiss_chat(request, chat_id):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())
    if not UserChatRelation.objects.filter(user_id=src.id, chat_id=chat_id, authority=1).exists():
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    chat = Chat(id=chat_id)
    chat.delete()
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user_chat_relation.delete()

    return OkResponse(OkDto())


def chat_invite_member(request, chat_id):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user = params.get('user')
    user_chat_relation = UserChatRelation(user_id=user.id, chat_id=chat_id)
    user_chat_relation.save()

    return OkResponse(OkDto())


def get_chat_member(request, chat_id):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    data = {"users": []}
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user = User.objects.get(id=user_chat_relation.user_id)
        data["users"].append({
            "username": user.username,
            "avatar": user.avatar
        })

    return OkResponse(OkDto(data=data))


def chat_remove_member(request, chat_id):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())
    if not UserChatRelation.objects.filter(user_id=src.id, chat_id=chat_id, authority=1).exists():
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user = params.get('user')
    user_chat_relation = UserChatRelation.objects.get(user_id=user.id, chat_id=chat_id)
    user_chat_relation.delete()

    return OkResponse(OkDto())


def leave_chat(request, chat_id):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user = params.get('user')
    user_chat_relation = UserChatRelation.objects.get(user_id=user.id, chat_id=chat_id)
    user_chat_relation.delete()

    return OkResponse(OkDto())
