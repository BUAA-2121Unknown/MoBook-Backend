# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 15:48
# @Author  : Tony Skywalker
# @File    : token_handler.py
#
import json

from live.models import ShareToken
from shared.utils.cache.cache_utils import first_or_default_by_cache, update_cached_object
from shared.utils.parameter.value_parser import parse_value
from shared.utils.token.base64_token import to_base64_token, from_base64_token
from shared.utils.token.exception import TokenException


def generate_share_token(item_id, proj_id):
    token = {"item": item_id, "proj": proj_id}
    return to_base64_token(json.dumps(token))


def parse_share_token(token):
    try:
        token = json.loads(from_base64_token(token))
        item_id = parse_value(token.get("item"), int)
        proj_id = parse_value(token.get("proj"), int)
    except Exception as e:
        raise TokenException("Invalid share token") from e
    return item_id, proj_id


def update_or_create_share_token(token, created, expires, auth):
    _, share_token = first_or_default_by_cache(ShareToken, token)
    share_token: ShareToken
    if share_token is None:
        share_token = ShareToken.create(token, created, expires, auth)
    else:
        share_token.created = created
        share_token.expires = expires
        share_token.auth = auth
        share_token.revoked = None
    share_token.save()
    update_cached_object(ShareToken, token, share_token)

    return share_token
