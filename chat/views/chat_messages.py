import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from user.models import User
from oauth.dtos.login_dto import LoginDto
from shared.dtos.OrdinaryResponseDto import BadRequestDto, ErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, OkResponse
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
#
#
# def send_message(request):
#     pass
