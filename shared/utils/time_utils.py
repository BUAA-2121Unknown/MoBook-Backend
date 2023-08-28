# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 11:52
# @Author  : Tony Skywalker
# @File    : time_utils.py
#
import datetime


def add_offset(timestamp: datetime.datetime):
    return timestamp.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
