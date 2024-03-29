# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/31/2023 12:05
# @Author  : Tony Skywalker
# @File    : cache_utils.py
#
import pickle

from django.core.cache import cache

from shared.utils.model.model_extension import first_or_default


def get_cache_key(model, pk):
    return model._meta.verbose_name + ":" + str(pk)  # 有问题


def first_or_default_by_cache(model, pk):
    key = get_cache_key(model, pk)
    pickled_obj = cache.get(key)
    if pickled_obj is None:
        obj = first_or_default(model, pk=pk)
        if obj is not None:
            cache.set(key, pickle.dumps(obj))
    else:
        obj = pickle.loads(pickled_obj)

    return key, obj


def update_cached_object(model, pk, obj):
    key = get_cache_key(model, pk)
    cache.set(key, pickle.dumps(obj))
    return key


def delete_cached_object(model, pk):
    key = get_cache_key(model, pk)
    cache.delete(key)
