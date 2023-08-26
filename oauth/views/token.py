# Create your views here.
from datetime import datetime

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from oauth.dtos.get_token_dto import GetTokenSuccessDto, GetTokenDto
from oauth.models import RefreshToken
from shared.dtos.ordinary_response_dto import BadRequestDto, UnauthorizedDto, InternalServerErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, UnauthorizedResponse, InternalServerErrorResponse, \
    OkResponse
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.parameter.parameter import parse_param
from shared.utils.token.jwt_token import generate_jwt_token
from shared.utils.token.refresh_token import generate_refresh_token


def _verify_user(uid, password):
    return True


@api_view(['POST'])
@csrf_exempt
def get_jwt_token(request):
    params = parse_param(request)
    try:
        dto: GetTokenDto = deserialize(params, GetTokenDto)
    except JsonDeserializeException as e:
        return BadRequestResponse(BadRequestDto("Request format error", data=e))
    if not _verify_user(dto.id, dto.password):
        return UnauthorizedResponse(UnauthorizedDto("Username or password error"))

    try:
        token = generate_jwt_token(dto.id)
        refresh_token = generate_refresh_token(dto.id)
        refresh_token.save()
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate JWT token", data=e))

    data = GetTokenSuccessDto(dto.id, token, refresh_token.expires)
    response = OkResponse(OkDto(data=data))

    # set cookies
    response.set_cookie(key="refreshToken", value=refresh_token.token, httponly=True)

    return response


@api_view(['POST'])
@csrf_exempt
def refresh_jwt_token(request):
    cookie = request.COOKIES.get("refreshToken", None)
    if cookie is None:
        return UnauthorizedResponse(UnauthorizedDto("Missing cookies: refreshToken"))

    refresh_token = first_or_default(RefreshToken, token=cookie)
    if refresh_token is None:
        return UnauthorizedResponse(UnauthorizedDto("Invalid refresh token"))
    if not refresh_token.is_active():
        return UnauthorizedResponse(UnauthorizedDto("Token not active"))
    refresh_token.revoked = timezone.now()
    refresh_token.save()

    uid = refresh_token.uid

    # generate new tokens
    try:
        token = generate_jwt_token(uid)
        new_refresh_token = generate_refresh_token(uid)
        new_refresh_token.save()
    except Exception as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to refresh token", data=e))

    data = GetTokenSuccessDto(uid, token, refresh_token.expires)
    response = OkResponse(OkDto(data=data))

    # set cookies
    response.set_cookie(key="refreshToken", value=new_refresh_token.token, httponly=True)

    return response


@api_view(['POST'])
@csrf_exempt
def revoke_jwt_token(request):
    cookie = request.COOKIES.get("refreshToken", None)
    if cookie is None:
        return OkResponse(OkDto("Cookies already revoked"))

    refresh_token: RefreshToken = first_or_default(RefreshToken, token=cookie)
    if refresh_token is None:
        return UnauthorizedResponse(UnauthorizedDto("Invalid refresh token"))
    if not refresh_token.is_active():
        return UnauthorizedResponse(UnauthorizedDto("Token not active"))
    refresh_token.revoked = timezone.now()
    refresh_token.save()

    response = OkResponse(OkDto("Token revoked"))
    response.delete_cookie("refreshToken")

    return response
