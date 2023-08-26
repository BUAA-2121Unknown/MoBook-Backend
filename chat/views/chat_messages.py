import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from message.models import Message
from shared.utils.model.user_extension import get_user_from_request
from user.models import User
from oauth.dtos.login_dto import LoginDto
from shared.dtos.ordinary_response_dto import BadRequestDto, ErrorDto, OkDto, UnauthorizedDto
from shared.response.json_response import BadRequestResponse, OkResponse, UnauthorizedResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def jump_to_at(request):
    pass


# @api_view(['POST'])
# @csrf_exempt
def get_chat_list(request):

    return render(request, 'index.html')


def get_messages(request, chat_id):
    # return history messages
    return render(request, 'chatroom.html', {'chat_id': chat_id})


def send_message(request, chat_id):
    user: User = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    # security check: in chat?
    message: Message = Message.create(src_id=user.id, chat_id=chat_id)  # 获得

    file = request.FILES.get('file')
    image = request.FILES.get('image')
    text = request.POST.get('text')
    if file is not None:
        message.file = file  # 组合方式
        message.type = 2
        message.text = file.url  # 本名
    elif image is not None:
        message.image = image
        message.type = 1
    elif text is not None:
        message.text = text
        message.type = 0
    else:
        return BadRequestResponse(BadRequestDto("Missing content"))

    message.save()
    # 返回文件路径
    return OkResponse(OkDto(data={
        'category': message.type,
        'text': message.text,
        'file_url': message.file.url,
        'src_id': user.id,
        'src_name': user.name,
        'src_avatar_url': user.avatar
    }))  # 需要返回文件的本名和url，前端（发送者）收到后进行ws请求






