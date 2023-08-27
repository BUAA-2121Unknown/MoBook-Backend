import json
import os

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from MoBook.settings import BASE_URL
from chat.models import Chat
from chat.utils.message_manager import new_to_chat, pull_older, new_to_chat_ver1, pull_newer
from message.models import Message
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.user_extension import get_user_from_request
from user.models import User, UserOrganizationProfile, UserChatRelation, UserChatJump
from oauth.dtos.login_dto import LoginDto
from shared.dtos.ordinary_response_dto import BadRequestDto, ErrorDto, OkDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, UnauthorizedResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
# at消息置顶？
def get_chat_list(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())

    user_chat_relation_list = UserChatRelation.objects.filter(user_id=user.id)  # 可能数据类型不匹配
    params = parse_param(request)
    data = {"chat_list": []}
    # 获取群聊列表：基础信息
    for user_chat_relation in user_chat_relation_list:
        chat = Chat.objects.get(chat_id=user_chat_relation.chat_id)
        tmp = {}
        tmp.append({
            "roomId": chat.id,
            "roomName": chat.chat_name,
            "unreadCount": user_chat_relation.unread,
            "avatar": BASE_URL + chat.chat_avatar.url,
        })

        # 获取最新at消息
        at_message_id = user_chat_relation.at_message_id

        # 判断是否覆盖：如果at_message_id是0表示已经失效
        if at_message_id != 0:
            message = Message.objects.get(message_id=at_message_id)
        else:
            message = Message.objects.get(message_id=chat.latest_message)
        tmp.append({"latest_message": {
            "content": message.text,
            "senderId": message.src_id,  # ?
            "username": UserOrganizationProfile.objects.get(user_id=message.src_id,
                                                            org_id=params.get("org_id")).nickname,
            "timestamp": message.timestamp.hour + ':' + message.timestamp.minute,
        }})  # 返回最新消息的数据：用户在组内昵称和消息文本

        tmp.append({"index": message.id})
        tmp.append({"users": [],
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
    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def search_messages(request):
    pass


@api_view(['POST'])
@csrf_exempt
def get_text_messages(request):
    pass


@api_view(['POST'])
@csrf_exempt
def get_image_messages(request):
    pass


@api_view(['POST'])
@csrf_exempt
def get_file_messages(request):
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

    chat = Chat.objects.get(id=chat_id)
    chat.latest_message = message.id
    chat.save()
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
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
    # security check: chat不存在。是否会拖慢速度？
    if not UserChatRelation.objects.filter(user_id=user.id, chat_id=chat_id).exists():
        return UnauthorizedResponse(UnauthorizedDto("Not in chat"))

    params = parse_param(request)
    type = params.get('type')  # 尝试get不存在的键不会报错
    response = {
        'src_id': user.id,
        'src_name': params.get('nickname'),  # 传过来团队内昵称
        'src_avatar_url': get_avatar_url("user", user.avatar),
    }

    message = Message(src_id=user.id, chat_id=chat_id)
    if params.get('type') is not None:
        text = params.get('type')
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
                user_chat_relation = UserChatRelation.objects.get(chat_id=chat_id)
                user_chat_relation.at_message_id = message.id
                user_chat_relation.save()
                user_chat_jump = UserChatJump(user_id=user_id, chat_id=chat_id, message_id=message.id, valid=1)
                user_chat_jump.save()

                # 发送at通知
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(str(user_id), {'type': 'notify', 'data': params.get('data')})

    else:
        return BadRequestResponse(BadRequestDto("Missing content"))

    # 更新最新消息
    chat = Chat.objects.get(id=chat_id)
    chat.latest_message = message.id
    chat.save()

    # 更新未读信息数目
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user_chat_relation.unread += 1
        user_chat_relation.save()
    message.save()
    return OkResponse(OkDto(data=response))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求
