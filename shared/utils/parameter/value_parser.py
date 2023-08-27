# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved
#
# @Time    : 8/23/2023 21:49
# @Author  : Tony Skywalker
# @File    : value_parser.py
#
# Description:
#   To parse explicit type of value form an unknown source value.
#

import datetime

from shared.utils.parameter.exceptions import ParameterException


def _default_or_exception(default, raise_on_error, msg):
    if raise_on_error:
        raise ParameterException(msg)
    return default


def _parse_value(val, _type, default, raise_on_error, strict):
    if val is None:
        return _default_or_exception(default, raise_on_error, "Value is None")
    try:
        if _type == datetime.datetime:
            if isinstance(val, str):
                return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            elif isinstance(val, datetime.datetime):
                return val
            else:
                return _default_or_exception(
                        default, raise_on_error, "Bad datetime.datetime format"
                )
        elif _type == datetime.date:
            if isinstance(val, str):
                _date = datetime.datetime.strptime(val, "%Y-%m-%d")
                return datetime.date(_date.year, _date.month, _date.day)
            elif isinstance(val, datetime.date):
                return val
            else:
                return _default_or_exception(
                        default, raise_on_error, "Bad datetime.date format"
                )
        else:
            if strict and not isinstance(val, _type):
                return _default_or_exception(
                        default, raise_on_error, f"Not strict match: {val} - [{_type}]"
                )
            return _type(val)
    except ValueError:
        return _default_or_exception(
                default, raise_on_error, f"Bad value type: {val} - [{_type}]"
        )


def parse_value(val, _type, default=None, raise_on_error=False):
    return _parse_value(val, _type, default, raise_on_error, False)


def parse_value_strict(val, _type, default=None, raise_on_error=False):
    return _parse_value(val, _type, default, raise_on_error, True)


def parse_value_with_check(val, _type, predicate=None, default=None, raise_on_error=False):
    try:
        value = parse_value(val, type, default, raise_on_error)
    except ParameterException as e:
        if raise_on_error:
            raise e
        return default
    if predicate is None:
        return value
    if predicate(value):
        return value
    if raise_on_error:
        raise ParameterException("Predicate failed")
    return default
