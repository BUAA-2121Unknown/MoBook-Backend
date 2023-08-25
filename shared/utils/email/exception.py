# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 9:57
# @Author  : Tony Skywalker
# @File    : exception.py
#

class EmailException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"Email Error: {self.msg}"
