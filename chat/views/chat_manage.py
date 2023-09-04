from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from chat.models import Chat, ChatType
from chat.utils.chat_manager import add_to_chat
from chat.utils.message_manager import _send_message
from org.models import Organization
from shared.dtos.ordinary_response_dto import UnauthorizedDto, OkDto
from shared.response.json_response import UnauthorizedResponse, OkResponse
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User, UserChatRelation, UserOrganizationProfile, U2U


@api_view(['POST'])
@csrf_exempt
def create_chat(request):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    # 建群
    org_id = params.get('org_id')
    invite_list = params.get('invite_list')
    if len(invite_list) == 1:
        # 判断存在
        type = ChatType.PRIVATE
        chat_name = ""
        if U2U.objects.filter(org_id=org_id, user1_id=src.id, user2_id=invite_list[0]["_id"]).exists():
            OkResponse(OkDto())
        if U2U.objects.filter(org_id=org_id, user2_id=src.id, user1_id=invite_list[0]["_id"]).exists():
            OkResponse(OkDto())
        u2u = U2U(org_id=org_id, user1_id=src.id, user2_id=invite_list[0]["_id"])
        u2u.save()
    else:
        type = ChatType.PUBLIC
        chat_name = "群聊"
    chat = Chat(org_id=org_id, type=type, chat_name=chat_name)
    chat.save()

    # 拉创始人
    add_to_chat(org_id=org_id, chat_id=chat.id, user_id=src.id, authority=1)

    # 拉所有人
    # add_to_chat(org_id=org_id, chat_id=chat.id, user_id=0, authority=0)

    # 拉n人
    for user_id in invite_list:
        # print(user_id)
        add_to_chat(org_id=org_id, chat_id=chat.id, user_id=user_id["_id"], authority=0)  #

    _send_message(src.id, "聊天创建成功", org_id, first_or_default(Organization, id=org_id), chat.id, chat, None, "系统", "", "", 1)

    return OkResponse(OkDto())


@api_view(['POST'])
@csrf_exempt
def upload_chat_avatar(request):
    src: User = get_user_from_request(request)
    if src is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    chat_id = params.get('chat_id')
    chat = first_or_default(Chat, chat_id=chat_id)
    chat.chat_avatar = request.FILES("chat_avatar")
    chat.save()


@api_view(['POST'])
@csrf_exempt
def dismiss_chat(request):
    params = parse_param(request)
    src: User = get_user_from_request(request)
    if src is None:
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
    user_id = params.get('user_id')
    org_id = params.get('org_id')
    chat_id = params.get('chat_id')
    add_to_chat(org_id=org_id, chat_id=chat_id, user_id=user_id, authority=0)
    chat = first_or_default(Chat, id=chat_id)
    _send_message(src.id, "欢迎新人入群", org_id, first_or_default(Organization, id=org_id), chat_id, chat, None,
                  "系统", "", "", 1)
    #  TODO: 和前端对接
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

    user_id = params.get('user_id')
    user_chat_relation = first_or_default(UserChatRelation, user_id=user_id, chat_id=params.get('chat_id'), org_id=params.get('org_id'))
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
