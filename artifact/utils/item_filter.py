# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 22:36
# @Author  : Tony Skywalker
# @File    : item_filter.py
#
import json
from typing import List

from artifact.models import ItemProperty


def filter_active_items(items: List[dict]):
    if items is None:
        return []

    result = []
    for item in items:
        data = item.get('data', None)
        _id = item.get('id', None)
        if data is None or _id is None:
            continue
        if data.get('status', -1) != 0:
            continue
        prop = data.get('prop', None)
        if prop is None:
            continue
        if prop in ItemProperty.dirs():
            children = filter_active_items(item.get('children', None))
            result.append({
                "data": data,
                "id": _id,
                "children": children
            })
        else:
            result.append({
                "data": data,
                "id": _id
            })

    return result


def filter_recycled_items(items: List[dict]):
    if items is None:
        return []

    result = []
    for item in items:
        data = item.get('data', None)
        _id = item.get('id', None)
        if data is None or _id is None:
            continue
        if data.get('status', -1) == 1:
            # add recycled item and stop recursion
            result.append({"data": data, "id": _id})
        else:
            # find deeper recycled items
            result.extend(filter_recycled_items(item.get('children', None)))

    return result
