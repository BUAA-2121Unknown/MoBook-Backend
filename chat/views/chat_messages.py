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
from message.models import Message
from shared.utils.model.user_extension import get_user_from_request
from user.models import User, UserOrganizationProfile, UserChatRelation, UserChatJump
from oauth.dtos.login_dto import LoginDto
from shared.dtos.OrdinaryResponseDto import BadRequestDto, ErrorDto, OkDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, UnauthorizedResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def jump_to_at(request):
    pass


@api_view(['POST'])
@csrf_exempt
def get_chat_list(request):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    chat_list = UserChatRelation.objects.filter(user_id=user.id)
    data = {"chat_list": []}
    for chat in chat_list:
        data["chat_list"].append({
            "chat_id": chat.chat_id,
            "chat_name": chat.chat_name,
            "chat_avatar": chat.chat_avatar,
        })
        at_message_id = UserChatRelation.objects.get(user_id=user.id, chat_id=chat.chat_id).at_message_id
        if UserChatJump(user_id=user.id, chat_id=chat.chat_id, at_message_id=at_message_id).valid == 1:
            data["chat_list"].append({"latest_message": at_message_id})
        else:
            data["chat_list"].append({"latest_message": chat.latest_message})

    return OkResponse(OkDto(data=data))


@api_view(['POST'])
@csrf_exempt
def get_messages(request, chat_id):  # unread = 0, valid = 0
    # return history messages
    return render(request, 'chatroom.html', {'chat_id': chat_id})


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
        'src_avatar_url': user.avatar
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
        message.save()
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
    type = params.get('type')
    response = {
        'src_id': user.id,
        'src_name': params.get('nickname'),  # 传过来团队内昵称
        'src_avatar_url': user.avatar,
    }

    message = Message(src_id=user.id, chat_id=chat_id)
    if 'text' in request.POST:
        text = request.POST['text']
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
                user_chat_relation = UserChatRelation.objects.get(chat_id=chat_id)
                user_chat_relation.at_message_id = message.id
                user_chat_relation.save()
                user_chat_jump = UserChatJump(user_id=user_id, chat_id=chat_id, message_id=message.id, valid=1)
                user_chat_jump.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.send)(user_id, {'type': 'notify', 'data': request.POST['data']})

    else:
        return BadRequestResponse(BadRequestDto("Missing content"))
    chat = Chat.objects.get(id=chat_id)
    chat.latest_message = message.id
    chat.save()
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id):
        user_chat_relation.unread += 1
        user_chat_relation.save()
    message.save()



