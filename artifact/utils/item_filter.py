# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 22:36
# @Author  : Tony Skywalker
# @File    : item_filter.py
#
from typing import List

from artifact.models import ItemProperty
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import Existence
from user.dtos.user_dto import UserDto
from user.models import User


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
        user_id = data.get('user_id', None)
        if user_id is None:
            continue
        data.pop('user_id', None)
        _, creator = first_or_default_by_cache(User, user_id)
        data['creator'] = None if creator is None else UserDto(creator)
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
            user_id = data.get('user_id', None)
            if user_id is None:
                continue
            data.pop('user_id', None)
            _, creator = first_or_default_by_cache(User, user_id)
            data['creator'] = None if creator is None else UserDto(creator)
            result.append({"data": data, "id": _id})
        else:
            # find deeper recycled items
            result.extend(filter_recycled_items(item.get('children', None)))

    return result


def filter_prototypes(items: List[dict], status: int):
    if items is None:
        return []

    result = []
    for item in items:
        data = item.get('data', None)
        _id = item.get('id', None)
        prop = data.get('prop', None)
        stat = data.get('status', None)
        if data is None or _id is None or prop is None or stat is None:
            continue

        if prop in ItemProperty.dirs():
            if stat == Existence.ACTIVE:
                result.extend(filter_prototypes(item.get('children', None), status))
        else:
            if prop in ItemProperty.prototypes() and stat == status:
                # find a prototype
                user_id = data.get('user_id', None)
                if user_id is None:
                    continue
                data.pop('user_id', None)
                _, creator = first_or_default_by_cache(User, user_id)
                data['creator'] = None if creator is None else UserDto(creator)
                result.append({"data": data, "id": _id})

    return result
