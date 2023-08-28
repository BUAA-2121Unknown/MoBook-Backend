# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 16:28
# @Author  : Tony Skywalker
# @File    : gererate_jwt_token_pair.py
#

from oauth.models import RefreshToken
from shared.dtos.ordinary_response_dto import InternalServerErrorDto
from shared.response.json_response import InternalServerErrorResponse
from shared.utils.token.exception import TokenException
from shared.utils.token.jwt_token import generate_jwt_token
from shared.utils.token.refresh_token import generate_refresh_token


def generate_jwt_token_pair(user_id: int):
    try:
        jwt_token = generate_jwt_token(user_id)
    except TokenException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate JWT token", data=e))

    candidates = [token for token in RefreshToken.objects.filter(uid=user_id).order_by("-expires") if token.is_active()]
    if len(candidates) == 0:
        # No candidates
        try:
            refresh_token = generate_refresh_token(user_id)
            refresh_token.save()
        except TokenException as e:
            return InternalServerErrorResponse(InternalServerErrorDto("Failed to generate refresh token", data=e))
    else:
        refresh_token = candidates[0]

    return jwt_token, refresh_token
