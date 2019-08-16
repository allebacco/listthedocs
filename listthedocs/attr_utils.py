import attr

from enum import Enum
from datetime import datetime
from typing import List, Union

from .datetime_utils import iso8601_to_datetime


def ListOf(element_type, default=attr.NOTHING):

    if attr.has(element_type):
        def converter(values: List[dict]):
            if values is None:
                return None
            return [element_type(**v) for v in values]
    else:
        def converter(values: list):
            if values is None:
                return None
            return [element_type(v) for v in values]

    return attr.ib(type=List[element_type], converter=converter, default=default)


def String(default=attr.NOTHING):
    return attr.ib(type=str, default=default)


def EnumString(enum: type):

    def converter(value: Union[str, enum]) -> str:
        if isinstance(value, str):
            return value
        return value.name

    return attr.ib(type=str, converter=converter)


def Bool():
    return attr.ib(type=bool)


def DateTime(default=attr.NOTHING):
    return attr.ib(type=datetime, converter=iso8601_to_datetime, default=default)


