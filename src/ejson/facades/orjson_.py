"""
ORJSON is the fastest JSON library for Python. Its speed VS standard library can range from 2 to 50 times
faster than the standard library JSON module when doing basic serialization/deserialization.

This library also supports the serialization natively of types like datetime, enums, dataclasses,
numpy and uuid, including the builtin JSON module supported types.

- serializes dataclass instances 40-50x as fast as other libraries
- serializes datetime, date, and time instances to RFC 3339 format, e.g., "1970-01-01T00:00:00+00:00"
- serializes numpy.ndarray instances 4-12x as fast with 0.3x the memory usage of other libraries
- pretty prints 10x to 20x as fast as the standard library
- serializes to bytes rather than str, i.e., is not a drop-in replacement
- serializes str without escaping unicode to ASCII, e.g., "好" rather than "\\u597d"
- serializes float 10x as fast and deserializes twice as fast as other libraries
- serializes subclasses of str, int, list, and dict natively, requiring default to specify how to serialize others
- serializes arbitrary types using a default hook
- has strict UTF-8 conformance, more correct than the standard library
- has strict JSON conformance in not supporting Nan/Infinity/-Infinity
- has an option for strict JSON conformance on 53-bit integers with default support for 64-bit
- does not provide load() or dump() functions for reading from/writing to file-like objects

https://github.com/ijl/orjson
"""
from __future__ import annotations
# TODO: check for packaging, requires rust: https://github.com/ijl/orjson#packaging


from collections import deque, defaultdict
from typing import Any, OrderedDict, Callable, Optional

import orjson as json
from bidict import bidict
from frozendict import frozendict

from empire_commons.types_ import NULL, JsonType


def default_encoder(obj: Any) -> JsonType:
    if obj == NULL:
        return "EMPIRE::NULL"
    elif isinstance(obj, (set, frozenset, deque)):
        return list(obj)
    elif isinstance(obj, (frozendict, bidict, OrderedDict, defaultdict)):
        return dict(obj)
    else:
        raise ValueError(f"Cannot serialize {obj}")


def dumps(
        obj: JsonType,
        *,
        default: Optional[Callable[[Any], Any]] = default_encoder,
        allow_non_string_keys: bool = False,
        append_new_line: bool = False,
        auto_serialize_dataclasses: bool = True,
        auto_serialize_datetime: bool = True,
        auto_serialize_subclasses_of_builtins: bool = True,
        pretty_print_2_spaces: bool = False,
        serialize_datetime_without_microseconds: bool = False,
        serialize_datetime_without_tzinfo: bool = False,
        serialize_numpy: bool = False,
        sort_keys: bool = False,
        strict_integers: bool = False,
        use_z_for_timezone: bool = False,
        **kwargs
) -> str:
    """
    Encode given Python obj instance into a JSON string.
    :param obj: the value to be serialized
    :param default: To serialize a subclass or arbitrary types, specify default as a callable that returns a supported type. default may be a function, lambda, or callable class instance. To specify that a type was not handled by default, raise an exception such as TypeError.
    :param allow_non_string_keys: (2x SLOWER when enabled) Serialize dict keys of type other than str. This allows dict keys to be one of str, int, float, bool, None, datetime.datetime, datetime.date, datetime.time, enum.Enum, and uuid.UUID. For comparison, the standard library serializes str, int, float, bool or None by default. orjson benchmarks as being faster at serializing non-str keys than other libraries. This option is slower for str keys than the default.
    :param append_new_line: Append \n to the output. This is a convenience and optimization for the pattern of dumps(...) + "\n". bytes objects are immutable and this pattern copies the original contents.
    :param auto_serialize_dataclasses: When disabled, passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower.
    :param auto_serialize_datetime: When disabled, passthrough datetime.datetime, datetime.date, and datetime.time instances to default. This allows serializing datetimes to a custom format, e.g., HTTP dates:
    :param auto_serialize_subclasses_of_builtins: When disabled, passthrough subclasses of builtin types to default. This does not affect serializing subclasses as dict keys if using OPT_NON_STR_KEYS.
    :param pretty_print_2_spaces: (0.25x SLOWER when enabled) Pretty-print output with an indent of two spaces. This is equivalent to indent=2 in the standard library. Pretty printing is slower and the output larger. orjson is the fastest compared library at pretty printing and has much less of a slowdown to pretty print than the standard library does. This option is compatible with all other options.
    :param serialize_datetime_without_microseconds: Do not serialize the microsecond field on datetime.datetime and datetime.time instances.
    :param serialize_datetime_without_tzinfo: Serialize datetime.datetime objects without a tzinfo as UTC. This has no effect on datetime.datetime objects that have tzinfo set.
    :param serialize_numpy: Serialize numpy.ndarray instances. For more, see `https://github.com/ijl/orjson#numpy`.
    :param sort_keys: (59% 5SLOWER when enabled) Serialize dict keys in sorted order. The default is to serialize in an unspecified order. This is equivalent to sort_keys=True in the standard library.
    :param strict_integers: Enforce 53-bit limit on integers. The limit is otherwise 64 bits, the same as the Python standard library. For more, see `https://github.com/ijl/orjson#int`.
    :param use_z_for_timezone: Serialize a UTC timezone on datetime.datetime instances as Z instead of +00:00.
    :return: A python str instance
    """
    options: int = 0

    if allow_non_string_keys:
        options |= json.OPT_NON_STR_KEYS

    if append_new_line:
        options |= json.OPT_APPEND_NEWLINE

    if not auto_serialize_dataclasses:
        options |= json.OPT_PASSTHROUGH_DATACLASS

    if not auto_serialize_datetime:
        options |= json.OPT_PASSTHROUGH_DATETIME

    if not auto_serialize_subclasses_of_builtins:
        options |= json.OPT_PASSTHROUGH_SUBCLASS

    if pretty_print_2_spaces:
        options |= json.OPT_INDENT_2

    if serialize_datetime_without_microseconds:
        options |= json.OPT_OMIT_MICROSECONDS

    if serialize_datetime_without_tzinfo:
        options |= json.OPT_NAIVE_UTC

    if serialize_numpy:
        options |= json.OPT_SERIALIZE_NUMPY

    if sort_keys:
        options |= json.OPT_SORT_KEYS

    if strict_integers:
        options |= json.OPT_STRICT_INTEGER

    if use_z_for_timezone:
        options |= json.OPT_UTC_Z

    data: bytes = json.dumps(obj, default=default, option=options)
    return data.decode("utf-8")


def loads(
        data: bytes | bytearray | memoryview | str,
        error_handler_: Callable[[str, json.JSONDecodeError], JsonType] | None = None,
        **kwargs
) -> JsonType:
    """
    loads() deserializes JSON to Python objects. It deserializes to dict, list, int, float, str, bool, and None objects.
    bytes, bytearray, memoryview, and str input are accepted. If the input exists as a memoryview, bytearray, or bytes object, it is recommended to
    pass these directly rather than creating an unnecessary str object. This has lower memory usage and lower latency.

    The input must be valid UTF-8.
    orjson maintains a cache of map keys for the duration of the process. This causes a net reduction in memory usage by avoiding duplicate strings.
    The keys must be at most 64 bytes to be cached and 512 entries are stored.

    The global interpreter lock (GIL) is held for the duration of the call.
    It raises JSONDecodeError if given an invalid type or invalid JSON. This includes if the input contains NaN, Infinity, or -Infinity, which the
    standard library allows, but is not valid JSON.

    JSONDecodeError is a subclass of json.JSONDecodeError and ValueError. This is for compatibility with the standard library.

    :param data: the JSON string to be deserialized
    :param error_handler_: In case the function is unable to decode *data*, it is sent to this handler
    :return: a Python object
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        if error_handler_ is not None:
            return error_handler_(data, e)
        raise

