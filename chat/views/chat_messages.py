from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from MoBook.settings import BASE_URL
from chat.models import Chat
from chat.utils.message_manager import new_to_chat, pull_older, new_to_chat_ver1, pull_newer
from message.models import Message
from notif.dtos.notif_payload import NotifAtPayload
from notif.utils.notif_manager import dispatch_notif
from org.models import Organization
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from user.models import User, UserOrganizationProfile, UserChatRelation, UserChatJump
from oauth.dtos.login_dto import LoginDto
from shared.dtos.ordinary_response_dto import BadRequestDto, ErrorDto, OkDto, UnauthorizedDto
from shared.dtos.ordinary_response_dto import BadRequestDto, OkDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, UnauthorizedResponse
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param
from user.models import User, UserChatRelation, UserChatJump


@api_view(['POST'])
@csrf_exempt
# at消息置顶？
def get_chat_list(request):  # org内的
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    params = parse_param(request)
    user_chat_relation_list = UserChatRelation.objects.filter(user_id=user.id, org_id=params.get("org_id"))  # 可能数据类型不匹配

    # 以上chat中，当前user所在的
    data = {"chat_list": []}
    # 获取群聊列表：基础信息
    for user_chat_relation in user_chat_relation_list:

        chat = first_or_default(Chat, id=user_chat_relation.chat_id)
        tmp = {
            "roomId": chat.id,
            "roomName": chat.chat_name,
            "unreadCount": user_chat_relation.unread,
            "avatar": BASE_URL + chat.chat_avatar.url,
        }

        # 获取最新at消息
        at_message_id = user_chat_relation.at_message_id

        # 判断是否覆盖：如果at_message_id是0表示已经失效
        if chat.latest_message != 0:
            if at_message_id != 0:
                message = first_or_default(Message, id=at_message_id)
            else:
                message = first_or_default(Message, id=chat.latest_message)
            tmp.update({"latest_message": {
                "content": message.text,
                "senderId": message.src_id,  # ?
                "username": first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                             org_id=params.get("org_id")).nickname,
                "timestamp": message.timestamp.hour + ':' + message.timestamp.minute,
                "index": message.id  # at消息置为很大的值
            }})  # 返回最新消息的数据：用户在组内昵称和消息文本
        else:
            tmp.update({"latest_message": {
                "content": "",
                "senderId": "",  # ?
                "username": "",
                "timestamp": "",
            }})
        tmp.update({"users": [],
                    "messages": []})
        data["chat_list"].append(tmp)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def get_all_messages(request, chat_id):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    data = new_to_chat_ver1(user, chat_id)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def view_chat(request, chat_id):  # unread = 0, valid = 0
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    data = new_to_chat(user, chat_id)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
# 需要分页
# 此时前端解除新消息锁定（ws）如果不行，就后端向前端发送ws通知
# 找到基准消息，
# 点击详情（最新），通知跳转（给id），at跳转（给id），搜索（返回匹配的消息列表（） + 给id跳转），刷新消息
# 点击详情和通知跳转会返回未读at消息列表并且进行清零
# 应该把获取消息（基于mid从底向上数）
def pull_older_messages(request, chat_id):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    message_id = params.get('message_id')
    message_num = params.get('message_num')
    data = pull_older(message_id, chat_id, message_num)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def pull_newer_messages(request, chat_id):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    message_id = params.get('message_id')
    message_num = params.get('message_num')
    data = pull_newer(message_id, chat_id, message_num)
    print(data)
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def search_messages(request):
    pass


@api_view(['POST'])
@csrf_exempt
def get_messages_by_type(request):
    pass


@api_view(['POST'])
@csrf_exempt
def send_file(request, chat_id):  # form data
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    # security check: chat不存在。是否会拖慢速度？
    if not UserChatRelation.objects.filter(user_id=user.id, chat_id=chat_id).exists():
        return UnauthorizedResponse(UnauthorizedDto("Not in chat"))

    params = parse_param(request)
    type = params.get('type')
    org_id = params.get('org_id')

    response = {
        'src_id': user.id,
        'src_name': params.get('nickname'),  # 传过来团队内昵称
        'src_avatar_url': get_avatar_url("user", user.avatar)
    }

    message = Message(src_id=user.id, chat_id=chat_id)

    if 'file' in request.FILES:
        file = request.FILES['file']
        message.file = file  # 组合方式
        message.type = 2
        message.text = file.name  # 本名
        message.save()
        response['text'] = file.name
        response['file_url'] = BASE_URL + message.file.url
        response['type'] = 2

    elif 'image' in request.FILES:
        image = request.FILES['image']
        message.image = image
        message.type = 1
        message.text = image.name
        message.save()
        response['text'] = image.name
        response['image_url'] = BASE_URL + message.image.url
        response['type'] = 1
    else:
        return BadRequestResponse(BadRequestDto("Missing content"))

    chat = first_or_default(Chat, id=chat_id)
    chat.latest_message = message.id
    chat.save()
    for user_chat_relation in first_or_default(UserChatRelation, chat_id=chat_id):
        user_chat_relation.unread += 1
        user_chat_relation.save()
    message.save()

    return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求


@api_view(['POST'])
@csrf_exempt
def send_text(request, chat_id):  # json
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    print(user.id)
    # security check: chat不存在。是否会拖慢速度？
    if not UserChatRelation.objects.filter(user_id=user.id, chat_id=chat_id).exists():
        return UnauthorizedResponse(UnauthorizedDto("Not in chat"))

    params = parse_param(request)
    type = params.get('type')  # 尝试get不存在的键不会报错
    org_id = params.get('org_id')
    org = first_or_default(Organization, id=org_id)
    chat = first_or_default(Chat, id=chat_id)

    response = {
        'src_id': user.id,
        'src_name': first_or_default(UserOrganizationProfile, user_id=user.id).nickname,  # 传过来团队内昵称
        'src_avatar_url': get_avatar_url("user", user.avatar),
    }

    message = Message(src_id=user.id, chat_id=chat_id)
    if params.get('text') is not None:
        text = params.get('text')
        message.text = text
        message.type = 0
        response['text'] = text
        response['type'] = 0
        message.save()
        if type == 3:
            response['type'] = 3
            message.type = 3
            at_list = params.get('at_list')  # user_id
            for user_id in at_list:
                # 更新at消息列表，群聊最新消息
                user_chat_relation = first_or_default(UserChatRelation, chat_id=chat_id)
                user_chat_relation.at_message_id = message.id
                user_chat_relation.save()
                user_chat_jump = UserChatJump(user_id=user_id, chat_id=chat_id, message_id=message.id, valid=1)
                user_chat_jump.save()

                notif_at_payload = NotifAtPayload(org, user, chat)
                dispatch_notif(user_id, org_id, notif_at_payload)

    else:
        return BadRequestResponse(BadRequestDto("Missing content"))

    # 更新最新消息

    chat.latest_message = message.id
    chat.save()

    # 更新未读信息数目
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user_chat_relation.unread += 1
        user_chat_relation.save()
    message.save()
    return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求
