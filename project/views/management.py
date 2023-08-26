# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 21:47
# @Author  : Tony Skywalker
# @File    : management.py
#
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project.dtos.create_project_dto import CreateProjectDto
from shared.dtos.ordinary_response_dto import UnauthorizedDto, BadRequestDto
from shared.response.json_response import UnauthorizedResponse, BadRequestResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.user_extension import get_user_from_request
from shared.utils.parameter.parameter import parse_param


@api_view(['POST'])
@csrf_exempt
def create_project(request):
    """
    {
        orgId: 1,
        name: "bbb",
        description: "bbb"
    }
    """
    user = get_user_from_request(request)
    if user is None:
        return UnauthorizedResponse(UnauthorizedDto())
    params = parse_param(request)
    try:
        dto: CreateProjectDto = deserialize(params, CreateProjectDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto(data=e))
    # org, uop = get_org_with_user(


@api_view(['POST'])
@csrf_exempt
def cancel_project(request):
    pass

# response = FileResponse(open(md_url, "rb"))
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(document.document_title + '.md'))
# return response
