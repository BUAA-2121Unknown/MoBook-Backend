from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from chat.models import Chat
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto
from shared.response.json_response import UnauthorizedResponse, OkResponse
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User, UserChatRelation


@api_view(['POST'])
@csrf_exempt
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
    user_chat_relation = UserChatRelation(user_id=src.id, chat_id=chat.id, authority=1, org_id=org_id)
    user_chat_relation.save()

    # 拉n人
    invite_list = params.get('invite_list')
    for user_id in invite_list:
        user_chat_relation = UserChatRelation(user_id=user_id, chat_id=chat.id, org_id=org_id)
        user_chat_relation.save()

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def dismiss_chat(request):
    params = parse_param(request)
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())
    if not UserChatRelation.objects.filter(user_id=src.id, chat_id=params.get('chat_id'), authority=1).exists():
        return UnauthorizedResponse(UnauthorizedDto())

    chat = Chat(id=params.get('chat_id'))
    chat.delete()
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=params.get('chat_id')):
        user_chat_relation.delete()

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def chat_invite_member(request):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user = params.get('user')
    user_chat_relation = UserChatRelation(user_id=user.id, chat_id=params.get('chat_id'), org_id=params.get('org_id'))
    user_chat_relation.save()

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def get_chat_members(request):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)

    return OkResponse(OkDto(data=get_chat_members(params.get('chat_id'), params.get('org_id'))))


@api_view(['POST'])
@csrf_exempt
def chat_remove_member(request):
    params = parse_param(request)
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())
    if not UserChatRelation.objects.filter(user_id=src.id, chat_id=params.get('chat_id'), authority=1).exists():
        return UnauthorizedResponse(UnauthorizedDto())

    user = params.get('user')
    user_chat_relation = first_or_default(UserChatRelation, user_id=user.id, chat_id=params.get('chat_id'))
    user_chat_relation.delete()

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def leave_chat(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user = params.get('user')
    user_chat_relation = first_or_default(UserChatRelation, user_id=user.id, chat_id=params.get('chat_id'))
    user_chat_relation.delete()

    return OkResponse(OkDto())
