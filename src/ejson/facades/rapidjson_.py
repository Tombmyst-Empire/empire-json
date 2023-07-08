from __future__ import annotations
import logging
from collections import deque, defaultdict
from datetime import datetime
from typing import Any, Callable, Optional, OrderedDict

import rapidjson as json
from bidict import bidict
from frozendict import frozendict
from rapidjson import JSONDecodeError

__all__ = ["json", "dumps", "loads", "JSONDecodeError"]

from empire_commons.types_ import NULL, JsonType


def default_encoder(obj: Any) -> JsonType:
    if obj == NULL:
        return "EMPIRE::NULL"
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (set, frozenset, tuple, deque)):
        return list(obj)
    elif isinstance(obj, (frozendict, bidict, OrderedDict, defaultdict)):
        return dict(obj)
    else:
        raise ValueError(f"Cannot serialize {obj}")


def dumps(
    obj: JsonType,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = False,
    write_mode: int = json.WM_COMPACT,
    indent: int | str = 4,
    default: Optional[Callable[[Any], JsonType]] = default_encoder,
    sort_keys: bool = False,
    number_mode: Optional[int] = None,
    datetime_mode: Optional[int] = None,
    uuid_mode: Optional[int] = None,
    bytes_mode: Optional[int] = json.BM_UTF8,
    iterable_mode: Optional[int] = json.IM_ANY_ITERABLE,
    mapping_mode: Optional[int] = json.MM_ANY_MAPPING,
    allow_nan: bool = True,
    **kwargs
) -> str:
    """
    Encode given Python obj instance into a JSON string.
    :param obj: the value to be serialized
    :param skipkeys: whether invalid dict keys will be skipped. If skipkeys is true (default: False), then dict keys that are not of a basic type
        (str, int, float, bool, None) will be skipped instead of raising a TypeError
    :param ensure_ascii: whether the output should contain only ASCII characters
    :param write_mode: enable particular pretty print behaviors
    :param indent: indentation width or string to produce pretty printed JSON
    :param default: a function that gets called for objects that can’t otherwise be serialized
    :param sort_keys: whether dictionary keys should be sorted alphabetically
    :param number_mode: enable particular behaviors in handling numbers
    :param datetime_mode: how should datetime, time and date instances be handled
    :param uuid_mode: how should UUID instances be handled
    :param bytes_mode: how should bytes instances be handled
    :param iterable_mode: how should iterable values be handled
    :param mapping_mode: how should mapping values be handled
    :param allow_nan: compatibility flag equivalent to number_mode=NM_NAN
    :returns: A Python str instance.
    """
    return json.dumps(
        obj,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        write_mode=write_mode,
        indent=indent,
        default=default,
        sort_keys=sort_keys,
        number_mode=number_mode,
        datetime_mode=datetime_mode,
        uuid_mode=uuid_mode,
        bytes_mode=bytes_mode,
        iterable_mode=iterable_mode,
        mapping_mode=mapping_mode,
        allow_nan=allow_nan,
    )


def loads(
    string: str,
    *,
    object_hook: Optional[Callable] = None,
    number_mode: int = None,
    datetime_mode: int = None,
    uuid_mode: int = None,
    parse_mode: int = None,
    allow_nan: bool = True,
    error_handler_: Optional[Callable[[str, json.JSONDecodeError], JsonType]] = None,
    **kwargs
) -> JsonType:
    """
    Decode the given JSON formatted value into Python object.
    :param string: The JSON string to parse, either a Unicode str instance or a bytes or a bytearray instance containing an UTF-8 encoded value
    :param object_hook: an optional function that will be called with the result of any object literal decoded (a dict) and should return the value to
     use instead of the dict
    :param number_mode: enable particular behaviors in handling numbers
    :param datetime_mode: how should datetime and date instances be handled
    :param uuid_mode: how should UUID instances be handled
    :param parse_mode: whether the parser should allow non-standard JSON extensions
    :param allow_nan: compatibility flag equivalent to number_mode=NM_NAN
    :param error_handler_: Error handler.
    :returns: An equivalent Python object.
    :raises ValueError: if an invalid argument is given
    :raises JSONDecodeError: if string is not a valid JSON value
    """
    try:
        return json.loads(
            string,
            object_hook=object_hook,
            number_mode=number_mode,
            datetime_mode=datetime_mode,
            uuid_mode=uuid_mode,
            parse_mode=parse_mode,
            allow_nan=allow_nan,
        )
    except json.JSONDecodeError as error:
        if error_handler_:
            return error_handler_(string, error)

        logging.debug("Bad JSON: %s", string)
        raise error
