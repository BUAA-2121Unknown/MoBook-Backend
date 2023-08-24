# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 23:21
# @Author  : Tony Skywalker
# @File    : model_extension.py
#

def first_or_default(model, *args, **kwargs):
    objs = model.objects.filter(*args, **kwargs)
    if objs.exists():
        return objs.first()
    return None
