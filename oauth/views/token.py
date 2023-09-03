# Create your views here.

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from oauth.dtos.get_token_dto import GetTokenSuccessDto, GetTokenDto
from oauth.models import RefreshToken
from oauth.utils.gererate_jwt_token_pair import generate_jwt_token_pair
from shared.dtos.ordinary_response_dto import BadRequestDto, UnauthorizedDto, InternalServerErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, UnauthorizedResponse, InternalServerErrorResponse, \
    OkResponse, NotFoundResponse
from shared.utils.cache.cache_utils import update_cached_object, first_or_default_by_cache
from shared.utils.json.exceptions import JsonDeserializeException
from shared.utils.json.serializer import deserialize
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.user_extension import get_user_by_id
from shared.utils.parameter.parameter import parse_param
from shared.utils.token.exception import TokenException
from shared.utils.token.jwt_token import generate_jwt_token
from shared.utils.token.password import verify_password
from shared.utils.token.refresh_token import generate_refresh_token
from user.dtos.error_dtos import NoSuchUserDto
from user.models import User


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

    user: User = get_user_by_id(dto.id)
    if user is None:
        return NotFoundResponse(NoSuchUserDto())
    if not user.activated:
        return UnauthorizedResponse(UnauthorizedDto("Not activated"))
    if not verify_password(dto.password, user.password):
        return UnauthorizedResponse(UnauthorizedDto("Wrong password"))

    # create JWT token and refresh token
    try:
        jwt_token, refresh_token = generate_jwt_token_pair(user.id)
    except TokenException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate JWT token", data=e))

    data = GetTokenSuccessDto(user.id, jwt_token, refresh_token.expires)
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

    _, refresh_token = first_or_default_by_cache(RefreshToken, cookie)
    if refresh_token is None:
        return UnauthorizedResponse(UnauthorizedDto("Invalid refresh token"))
    if not refresh_token.is_active():
        return UnauthorizedResponse(UnauthorizedDto("Token not active"))
    refresh_token.revoked = timezone.now()
    refresh_token.save()

    update_cached_object(RefreshToken, refresh_token.token, refresh_token)

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

    update_cached_object(RefreshToken, refresh_token.token, refresh_token)

    response = OkResponse(OkDto("Token revoked"))
    response.delete_cookie("refreshToken")

    return response
