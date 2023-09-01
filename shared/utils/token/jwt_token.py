# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 22:54
# @Author  : Tony Skywalker
# @File    : jwt_token.py
#

from datetime import datetime, timedelta

import jwt

from MoBook import settings
from shared.utils.token.exception import TokenException

HEADER = {
    'alg': 'HS256',
    'typ': 'JWT'
}

KEY = settings.SECRETS['signing']['key']
SALT = settings.SECRETS['signing']['salt']


def generate_jwt_token(data):
    payload = {
        'data': data,
        'exp': datetime.utcnow() + timedelta(1209600.0)
    }
    try:
        token = jwt.encode(payload, key=KEY, headers=HEADER).decode('UTF-8')
    except Exception as e:
        raise TokenException("Failed to generate JWT token") from e
    return token


def verify_jwt_token(token: str):
    payload = None
    if token is None:
        raise TokenException("Missing JWT token")
    token = token.split(' ')[-1]
    try:
        payload = jwt.decode(token.encode('UTF-8'), key=KEY, algorithms='HS256')
    except jwt.exceptions.DecodeError as e:
        raise TokenException("Failed to verify JWT token") from e
    except jwt.exceptions.ExpiredSignatureError as e:
        raise TokenException("JWT token expired") from e
    except jwt.exceptions.InvalidAlgorithmError as e:
        raise TokenException("Invalid JWT algorithm") from e
    data = None
    if payload:
        data = payload.get('data', None)
    if data is None:
        raise TokenException("Invalid JWT data")
    return data
