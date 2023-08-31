# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 20:05
# @Author  : Tony Skywalker
# @File    : authorize.py
#
from live.dto.authorize_dto import AuthorizeData
from live.models import ShareToken, ShareAuth
from live.utils.token_handler import parse_share_token
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_with_user
from shared.utils.model.project_extension import get_proj_and_org
from user.models import User


def authorize_share_token_aux(token, user: User):
    if token is None:
        return AuthorizeData(ShareAuth.DENIED, "No token")
    share_token: ShareToken = first_or_default_by_cache(ShareToken, token)
    if share_token is None:
        return AuthorizeData(ShareAuth.DENIED, "Invalid token")
    if not share_token.is_active():
        return AuthorizeData(ShareAuth.DENIED, "Token expired or revoked")

    # now, token is active
    if not share_token.org_only:
        return AuthorizeData(share_token.auth, "Permission granted")

    if user is None:
        return AuthorizeData(ShareAuth.DENIED, "Organization only")

    item_id, proj_id = parse_share_token(token)
    proj, org, error = get_proj_and_org(proj_id, user)
    if error is not None:
        return AuthorizeData(ShareAuth.DENIED, "Not in project")

    return AuthorizeData(share_token.auth, "Permission granted")
