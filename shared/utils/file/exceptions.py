# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 11:02
# @Author  : Tony Skywalker
# @File    : exceptions.py
#

class FileException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"File Error: {self.msg}"
