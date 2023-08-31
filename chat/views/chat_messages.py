import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from MoBook.settings import BASE_URL
from chat.models import Chat, ChatType, ChatAvatar
from chat.utils.message_manager import new_to_chat, pull_older, new_to_chat_ver1, pull_newer
from message.models import Message
from notif.dtos.notif_payload import NotifAtPayload
from notif.utils.notif_manager import dispatch_notification
from org.models import Organization
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.dir_utils import get_avatar_url
from shared.utils.file.file_handler import parse_filename
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.time_utils import get_date, get_time
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
        }
        if chat.type == ChatType.ORG:
            tmp["avatar"] = get_avatar_url("org", org.avatar)
        elif chat.type == ChatType.PUBLIC:
            tmp["avatar"] = BASE_URL + ChatAvatar.DEFAULT
        else:  # 另外一个人的头像
            for uc in user_chat_relation.objects.filter(chat_id=user_chat_relation.chat_id):
                if uc.user_id != user.id:
                    tmp["avatar"] = get_avatar_url("user", first_or_default(User, id=uc.user_id))

        # 获取最新at消息
        at_message_id = user_chat_relation.at_message_id

        # 判断是否覆盖：如果at_message_id是0表示已经失效
        if chat.latest_message != 0:
            if at_message_id != 0:
                message = first_or_default(Message, id=at_message_id)
            else:
                message = first_or_default(Message, id=chat.latest_message)
            tmp.update({"lastMessage": {
                "content": message.text,
                "senderId": str(message.src_id),  # ?
                "username": first_or_default(UserOrganizationProfile, user_id=message.src_id,
                                             org_id=params.get("org_id")).nickname,
                "timestamp": get_time(message.timestamp),
                "date": get_date(message.timestamp),

                "saved": True,
                "distributed": True,
                "seen": True,
            }})  # 返回最新消息的数据：用户在组内昵称和消息文本
        else:
            tmp.update({"lastMessage": {
                "content": "",
                "senderId": "",  # ?
                "username": "",
                "timestamp": "",
            }})

        tmp.update({"users": [],
                    "messages": [],
                    "index": chat.latest_message  # at消息置为很大的值 TODO:
                    })
        data["chat_list"].append(tmp)

    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def get_all_messages(request):
    params = parse_param(request)
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    print(user.id)
    print(params.get('chat_id'))
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
    pass


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
    # security check: chat不存在。是否会拖慢速度？
    if not UserChatRelation.objects.filter(user_id=user.id, chat_id=params.get('chat_id')).exists():
        return UnauthorizedResponse(UnauthorizedDto("Not in chat"))

    text = params.get('text')
    org_id = params.get('org_id')
    
    org = first_or_default_by_cache(Organization, org_id)
    chat = first_or_default(Chat, id=params.get('chat_id'))

    response = {
        "senderId": user.id,
        "username": first_or_default(UserOrganizationProfile, user_id=user.id).nickname,  # 传过来团队内昵称
        "avatar": get_avatar_url("user", user.avatar),  # TODO: 可以前端存储
        "saved": True,
        "distributed": True,
        "seen": True,
    }

    message = Message(src_id=user.id, chat_id=params.get('chat_id'))
    if 'file' in request.FILES:
        file = request.FILES['file']
        file.name = file.name + "." + extension
        message.file = file  # 组合方式
        message.text = file.name  # 本名
        message.type = 1  # TODO: 预留
        message.save()
        response['content'] = file.name
        response["files"] = []
        response['files'].append({
            "name": file.name,
            "size": 0,  # TODO: 预留
            "type": extension,
            "audio": False,  # TODO: 预留
            "duration": 0,  # TODO: 预留
            "url": BASE_URL + message.file.url,
            # preview
            # "progress": 100,  # TODO: 预留
        })
    if text is not None:
        message.text = text
        message.type = 0
        response['content'] = text
        message.save()
        if at_list is not None:
            message.type = 3
            for user_id in at_list:
                # 更新at消息列表，群聊最新消息
                user_chat_relation = first_or_default(UserChatRelation, chat_id=params.get('chat_id'))
                user_chat_relation.at_message_id = message.id
                user_chat_relation.save()
                user_chat_jump = UserChatJump(user_id=user_id, chat_id=params.get('chat_id'), message_id=message.id,
                                              valid=1)
                user_chat_jump.save()

                notif_at_payload = NotifAtPayload(org, user, chat)
                dispatch_notification(user_id, org_id, notif_at_payload)

                response["at_list"] = at_list
    response.update({
        "_id": message.id,
        "indexId": 0,  # TODO: 预留
        "timestamp": get_time(message.timestamp),
        "date": get_date(message.timestamp),
    })
    if 'file' not in request.FILES and text is None:
        return BadRequestResponse(BadRequestDto("Missing content"))

    # 更新最新消息

    chat.latest_message = message.id
    chat.save()

    # 更新未读信息数目

    for user_chat_relation in UserChatRelation.objects.filter(chat_id=params.get('chat_id')):
        user_chat_relation.unread += 1

        user_chat_relation.save()
    message.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(str(chat.id), {
        'type': 'chat_message',
        'data': response
    })

    return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求

#
# @api_view(['POST'])
# @csrf_exempt
# def send_file(request):  # form data
#     params = parse_param(request)
#     print(params)
#     user: User = get_user_from_request(request)
#     if user is None:
#         return UnauthorizedResponse(UnauthorizedDto())
#     # security check: chat不存在。是否会拖慢速度？
#     if not UserChatRelation.objects.filter(user_id=user.id, chat_id=params.get('chat_id')).exists():
#         return UnauthorizedResponse(UnauthorizedDto("Not in chat"))
#
#     params = parse_param(request)
#     category = params.get('category')
#     org_id = params.get('org_id')
#
#     response = {
#         'src_id': user.id,
#         'src_name': first_or_default(UserOrganizationProfile, user_id=user.id,
#                                      org_id=params.get("org_id")).nickname,  # 传过来团队内昵称
#         'src_avatar_url': get_avatar_url("user", user.avatar)
#     }
#
#     message = Message(src_id=user.id, chat_id=params.get('chat_id'))
#
#     if 'file' in request.FILES:
#         file = request.FILES['file']
#         file.name = file.name + "." + params.get("extension")
#         message.file = file  # 组合方式
#         message.type = 2
#         message.text = file.name  # 本名
#         message.save()
#         response['text'] = file.name
#         response['file_url'] = BASE_URL + message.file.url
#         response['category'] = 2
#
#     elif 'image' in request.FILES:
#         image = request.FILES['image']
#         image.name += "." + params.get("extension")
#         message.image = image
#         message.type = 1
#         message.text = image.name
#         message.save()
#         response['text'] = image.name
#         response['image_url'] = BASE_URL + message.image.url + "." + params.get("extension")
#         response['category'] = 1
#     else:
#         return BadRequestResponse(BadRequestDto("Missing content"))
#
#     chat = first_or_default(Chat, id=params.get('chat_id'))
#     chat.latest_message = message.id
#     chat.save()
#     for user_chat_relation in UserChatRelation.objects.filter(chat_id=params.get('chat_id')):
#         user_chat_relation.unread += 1
#         user_chat_relation.save()
#     message.save()
#
#     return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求
#
#
# @api_view(['POST'])
# @csrf_exempt
# def send_text(request):  # json
#     params = parse_param(request)
#     user: User = get_user_from_request(request)
#     if user is None:
#         return UnauthorizedResponse(UnauthorizedDto())
#     # security check: chat不存在。是否会拖慢速度？
#     if not UserChatRelation.objects.filter(user_id=user.id, chat_id=params.get('chat_id')).exists():
#         return UnauthorizedResponse(UnauthorizedDto("Not in chat"))
#
#     params = parse_param(request)
#     category = params.get('category')  # 尝试get不存在的键不会报错
#     org_id = params.get('org_id')
#     org = first_or_default(Organization, id=org_id)
#     chat = first_or_default(Chat, id=params.get('chat_id'))
#
#     response = {
#         "senderId": user.id,
#         "username": first_or_default(UserOrganizationProfile, user_id=user.id).nickname,  # 传过来团队内昵称
#         "avatar": get_avatar_url("user", user.avatar),
#         "saved": True,
#         "distributed": True,
#         "seen": True,
#     }
#
#     message = Message(src_id=user.id, chat_id=params.get('chat_id'))
#     if params.get('text') is not None:
#         text = params.get('text')
#         message.text = text
#
#         message.type = 0
#         response['content'] = text
#         # response['category'] = 0
#
#         message.save()
#         response.update({
#             "_id": message.id,
#             "timestamp": get_time(message.timestamp),
#             "date": get_date(message.timestamp),
#
#         })
#         if category == 3:
#             # response['category'] = 3
#             message.type = 3
#             at_list = params.get('at_list')  # user_id
#             for user_id in at_list:
#                 # 更新at消息列表，群聊最新消息
#                 user_chat_relation = first_or_default(UserChatRelation, chat_id=params.get('chat_id'))
#                 user_chat_relation.at_message_id = message.id
#                 user_chat_relation.save()
#                 user_chat_jump = UserChatJump(user_id=user_id, chat_id=params.get('chat_id'), message_id=message.id,
#                                               valid=1)
#                 user_chat_jump.save()
#
#                 notif_at_payload = NotifAtPayload(org, user, chat)
#                 dispatch_notification(user_id, org_id, notif_at_payload)
#
#     else:
#         return BadRequestResponse(BadRequestDto("Missing content"))
#
#     # 更新最新消息
#
#     chat.latest_message = message.id
#     chat.save()
#
#     # 更新未读信息数目
#
#     for user_chat_relation in UserChatRelation.objects.filter(chat_id=params.get('chat_id')):
#         user_chat_relation.unread += 1
#
#         user_chat_relation.save()
#     message.save()
#
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(str(chat.id), {
#         'type': 'chat_message',
#         'data': response
#     })
#
#     return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求
