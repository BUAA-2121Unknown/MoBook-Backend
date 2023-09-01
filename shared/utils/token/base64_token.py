# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 15:07
# @Author  : Tony Skywalker
# @File    : base64_token.py
#
# Description:
#   Must be ASCII string.
#
import base64


def to_base64_token(plain_utf8: str) -> str:
    plain_bytes = plain_utf8.encode("utf-8")
    base64_bytes = base64.b64encode(plain_bytes)
    base64_ascii = base64_bytes.decode("utf-8")
    return base64_ascii


def from_base64_token(base64_utf8: str) -> str:
    base64_bytes = base64_utf8.encode("utf-8")
    plain_bytes = base64.b64decode(base64_bytes)
    plain_utf8 = plain_bytes.decode("utf-8")
    return plain_utf8
