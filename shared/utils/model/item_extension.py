# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 10:06
# @Author  : Tony Skywalker
# @File    : item_extension.py
#
from artifact.models import Item


def get_item_lambda():
    return lambda node_id: Item.objects.get(pk=node_id)
