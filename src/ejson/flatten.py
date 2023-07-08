from __future__ import annotations

from typing import Callable

from empire_commons.types_ import JsonType

FlattenerType = Callable[[JsonType], JsonType]


def _flatten_object(
    data: dict,
    object_keys_separator: str,
    array_subscript_separator: str,
    *,
    no_index_for_arrays: bool,
    prefix: str = "",
    flatten_arrays: bool = True,
) -> JsonType:
    def make_prefix(key: str) -> str:
        if prefix.endswith(array_subscript_separator[-1]):
            return f"{prefix}{key}"
        elif prefix:
            return f"{prefix}{object_keys_separator}{key}"
        else:
            return f"{key}"

    flattened: JsonType = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flattened.update(
                _flatten_object(
                    value,
                    object_keys_separator,
                    array_subscript_separator,
                    prefix=make_prefix(key),
                    flatten_arrays=flatten_arrays,
                    no_index_for_arrays=no_index_for_arrays,
                )
            )
        elif flatten_arrays and isinstance(value, list):
            flattened.update(
                _flatten_array(
                    value,
                    object_keys_separator,
                    array_subscript_separator,
                    prefix=make_prefix(key),
                    flatten_arrays=flatten_arrays,
                    no_index_for_arrays=no_index_for_arrays,
                )
            )
        else:
            flattened[make_prefix(key)] = value
    return flattened


def _flatten_array(
    data: list,
    object_keys_separator: str,
    array_subscript_separator: str,
    *,
    no_index_for_arrays: bool,
    prefix: str = "",
    flatten_arrays: bool = True,
) -> JsonType:
    def make_prefix(index: int, *, primitive_value: bool = False) -> str:
        if no_index_for_arrays:
            return f"{prefix}{array_subscript_separator}"
        elif "%d" in array_subscript_separator:
            return f"{prefix}{array_subscript_separator}" % index
        elif prefix:
            return f"{prefix}{array_subscript_separator}{index}{array_subscript_separator}"
        elif primitive_value:
            return f"{index}"
        else:
            return f"{index}{array_subscript_separator}"

    flattened: JsonType = {}
    for index, value in enumerate(data):
        if isinstance(value, dict):
            flattened.update(
                _flatten_object(
                    value,
                    object_keys_separator,
                    array_subscript_separator,
                    prefix=make_prefix(index),
                    flatten_arrays=flatten_arrays,
                    no_index_for_arrays=no_index_for_arrays,
                )
            )
        elif flatten_arrays and isinstance(value, list):
            flattened.update(
                _flatten_array(
                    value,
                    object_keys_separator,
                    array_subscript_separator,
                    prefix=make_prefix(index),
                    flatten_arrays=flatten_arrays,
                    no_index_for_arrays=no_index_for_arrays,
                )
            )
        else:
            flattened[make_prefix(index, primitive_value=True)] = value
    return flattened


def get_flattener(
    *,
    root_identifier: str = "",
    object_keys_separator: str = ".",
    array_subscript_separator: str = "[%d]",
    flatten_arrays: bool = True,
    no_index_for_arrays: bool = False,
):
    """
    Returns a function that flattens a JSON object, with the provided configuration

    :param root_identifier: If provided, will prepend the flattened keys with this value
    :param object_keys_separator: The separator for object keys
    :param array_subscript_separator: The separator for array indices
    :param flatten_arrays: If True, will flatten arrays as well otherwise will leave them as is
    :param no_index_for_arrays: If True, when flattening arrays, the produced keys won't contain any reference of the index.
    """

    def flatten(data: JsonType) -> JsonType:
        """
        Flattens a JSON object
        """
        if not object_keys_separator:
            raise ValueError("object_keys_separator cannot be empty")

        if not array_subscript_separator:
            raise ValueError("array_subscript_separator cannot be empty")

        if isinstance(data, dict):
            return _flatten_object(
                data,
                object_keys_separator,
                array_subscript_separator,
                prefix=root_identifier,
                flatten_arrays=flatten_arrays,
                no_index_for_arrays=no_index_for_arrays,
            )
        elif flatten_arrays and isinstance(data, list):
            return _flatten_array(
                data,
                object_keys_separator,
                array_subscript_separator,
                prefix=root_identifier,
                flatten_arrays=flatten_arrays,
                no_index_for_arrays=no_index_for_arrays,
            )
        else:
            return data

    return flatten


DEFAULT_FLATTENER = get_flattener()  #: Default flattener instantiated. See :func:`get_flattener` for reference.
