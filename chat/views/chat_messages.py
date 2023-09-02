import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer, channel_layers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from thefuzz import fuzz

from MoBook.settings import BASE_URL
from chat.consumers import ChatsConsumer, ChatMessageConsumer
from chat.models import Chat, ChatType, ChatAvatar
from chat.utils.chat_manager import _get_chat_members
from chat.utils.message_manager import new_to_chat, pull_older, new_to_chat_ver1, pull_newer, pull_message, \
    _send_message
from message.models import Message
from notif.dtos.notif_payload import NotifAtPayload
from notif.utils.notif_manager import dispatch_notification
from org.models import Organization
from shared.dtos.ordinary_response_dto import BadRequestDto, OkDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, UnauthorizedResponse
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from shared.utils.time_utils import get_date, get_time
from user.models import User, UserChatRelation, UserChatJump, UserAuth
from user.models import UserOrganizationProfile


@api_view(['POST'])
@csrf_exempt
# at消息置顶？
def get_chat_list(request):  # org内的
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    org_id = params.get("org_id")
    org = first_or_default(Organization, id=org_id)
    user_chat_relation_list = UserChatRelation.objects.filter(user_id=user.id, org_id=org_id)  # 可能数据类型不匹配
    # 以上chat中，当前user所在的
    data = {"chat_list": []}
    # 获取群聊列表：基础信息
    for user_chat_relation in user_chat_relation_list:

        chat = first_or_default(Chat, id=user_chat_relation.chat_id)
        tmp = {
            "roomId": chat.id,
            "roomName": chat.chat_name,
            "unreadCount": user_chat_relation.unread,
            "room_type": chat.type
        }
        if chat.type == ChatType.ORG:
            tmp["avatar"] = get_avatar_url("org", org.avatar)
        elif chat.type == ChatType.PUBLIC:
            tmp["avatar"] = BASE_URL + ChatAvatar.DEFAULT
        else:  # 另外一个人的头像
            for uc in UserChatRelation.objects.filter(chat_id=chat.id):

                if uc.user_id != user.id:

                    tmp["avatar"] = get_avatar_url("user", first_or_default(User, id=uc.user_id).avatar)
                    tmp["roomName"] = first_or_default(UserOrganizationProfile, user_id=uc.user_id,
                                                       org_id=org_id).nickname

        # 获取最新at消息
        at_message_id = user_chat_relation.at_message_id

        # 判断是否覆盖：如果at_message_id是0表示已经失效
        if chat.latest_message != 0:
            # if at_message_id != 0:
            #     message = first_or_default(Message, id=at_message_id)
            # else:
            #     message = first_or_default(Message, id=chat.latest_message)
            message = first_or_default(Message, id=chat.latest_message)
            user_organization_profile = first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                                         org_id=params.get("org_id"))
            if user_organization_profile is not None:
                nickname = user_organization_profile.nickname
            else:
                nickname = ""
            tmp.update({"lastMessage": {
                "content": message.text,
                "senderId": str(message.src_id),  # ?
                "username": nickname,
                "timestamp": get_time(message.timestamp),
                "date": get_date(message.timestamp),

                "saved": False,
                "distributed": False,
                "seen": False,
                "system": bool(message.is_system)
            }})  # 返回最新消息的数据：用户在组内昵称和消息文本
            if message.is_system == 1:
                tmp["lastMessage"]["username"] = ""
                tmp["lastMessage"]["senderId"] = ""
        else:
            tmp.update({"lastMessage": {
                "content": "",
                "senderId": "",  # ?
                "username": "",
                "timestamp": "",
            }})

        tmp.update({"users": [],
                    "messages": [],
                    "index": chat.latest_message
                    })
        tmp.update(_get_chat_members(chat.id, org_id, user.id))
        data["chat_list"].append(tmp)
    data["all_users"] = []
    for user_org_relation in UserOrganizationProfile.objects.filter(org_id=org_id):
        user = first_or_default(User, id=user_org_relation.user_id)
        data["all_users"].append({  # at渲染是根据这个吗？
            "_id": str(user.id),
            "username": first_or_default(UserOrganizationProfile, user_id=user.id,
                                         org_id=org_id).nickname,
            "avatar": get_avatar_url("user", user.avatar),
        })
    user_org_relation = first_or_default(UserOrganizationProfile, org_id=org_id, user_id=user.id)
    data["all_users"].append({
        "_id": str(0),
        "username": "所有人",
        "avatar": "",
    })
    # ?
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def get_all_messages(request):
    params = parse_param(request)
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    data = new_to_chat_ver1(user, params.get('chat_id'), params.get('org_id'))
    data.update()
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def view_chat(request):  # unread = 0, valid = 0
    params = parse_param(request)
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    data = new_to_chat(user, params.get('chat_id'), params.get('org_id'))
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
# 需要分页
# 此时前端解除新消息锁定（ws）如果不行，就后端向前端发送ws通知
# 找到基准消息，
# 点击详情（最新），通知跳转（给id），at跳转（给id），搜索（返回匹配的消息列表（） + 给id跳转），刷新消息
# 点击详情和通知跳转会返回未读at消息列表并且进行清零
# 应该把获取消息（基于mid从底向上数）
def pull_older_messages(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    message_id = params.get('message_id')
    message_num = params.get('message_num')
    data = pull_older(message_id, params.get('chat_id'), message_num, params.get('org_id'))
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def pull_newer_messages(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    message_id = params.get('message_id')
    message_num = params.get('message_num')
    data = pull_newer(message_id, params.get('chat_id'), message_num, params.get('org_id'))
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def search_messages(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    src = params.get('search')
    num = params.get('num')
    org_id = params.get('org_id')
    chat_id = params.get('chat_id')
    messages = Message.objects.filter(chat_id=chat_id)
    res = sorted(messages, key=lambda x: -fuzz.partial_token_sort_ratio(src, x.text))[:int(num)]
    # print(src)
    # for message in res:
    #     print(message.text)
    #     print(fuzz.token_sort_ratio(src, message.text))
    return OkResponse(OkDto(data=pull_message(res, org_id)))


@api_view(['POST'])
@csrf_exempt
def get_messages_by_type(request):
    pass


@api_view(['POST'])
@csrf_exempt
def send_message(request):  # form data
    params = parse_param(request)

    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    text = params.get('text')
    org_id = parse_value(params.get('org_id'), int)
    org = first_or_default(Organization, id=org_id)
    chat_id = parse_value(params.get('chat_id'), int)
    chat = first_or_default(Chat, id=chat_id)
    extension = params.get('extension')
    at_list = params.get('at_list')
    pattern = r"<usertag>(\d+)</usertag>"
    if text is not None:
        matches = re.findall(pattern, text)
        at_list = [int(match) for match in matches]
        if len(at_list) != 0 and at_list[0] == 0:
            at_list = [x.user_id for x in UserChatRelation.objects.filter(org_id=org_id, chat_id=chat_id)]
    # 将匹配到的数字转换为整数，并存储在数组中

    nickname = first_or_default(UserOrganizationProfile, user_id=user.id, org_id=org_id).nickname
    if 'file' in request.FILES:
        file = request.FILES['file']
    else:
        file = ""
    response = _send_message(user.id, text, org_id, org, chat_id, chat, at_list, nickname, extension, file, 0)

    return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求
