# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/23/2023 21:40
# @Author  : Tony Skywalker
# @File    : exceptions.py


class ParameterException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"Bad Parameter: {self.msg}"
