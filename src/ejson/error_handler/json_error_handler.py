"""
Module that attempts to fix erroneous JSON.
"""
from __future__ import annotations
import logging
from typing import Any, Final, Optional

import rapidjson as json

from ejson.error_handler.cases import (
    invalid_value,
    missing_comma_or_curly_bracket_after_object_member,
    missing_name_for_object_member, unexpected_control_character_in_string,
)
from ejson.error_handler.handled_json_error import HandledJSONError
from ejson.error_handler.util import get_offset_from_error_string
from empire_commons.types_ import JsonType

_MAXIMUM_DEPTH: Final[int] = 20


# TODO: perform QA of this function
# TODO: build tests
def error_handler(to_decode: str, error: json.JSONDecodeError, depth: int = 0) -> JsonType:
    """
    This function attempts to fix erroneous JSON while decoding it, which usually occurs when json.loads() function.

    :param to_decode: The JSON string to parse
    :param error: The exception instance
    :param depth: You don't have to provide this value, used to avoid infinite recursion
    :return: Always returns the parsed JSON, on error, it simply raise it.
    :raises: Any exception that may occur while parsing the JSON.
    """
    character_index: Optional[int] = get_offset_from_error_string(str(error))
    if character_index is not None:
        character_message: str = f'Problematic character at index {character_index}: {to_decode[character_index - 10:character_index + 10]}'
        logging.info(character_message)
        logging.debug((len(character_message) - 10) * '.' + '^')

    try:
        if depth < _MAXIMUM_DEPTH:
            error_string: str = str(error)
            if "Missing a name for object member" in error_string:
                return missing_name_for_object_member(to_decode, depth)
            elif "Invalid value" in error_string:
                return invalid_value(to_decode, depth)
            elif "Missing a comma or '}' after an object member" in error_string:
                return missing_comma_or_curly_bracket_after_object_member(to_decode, depth)
            elif 'unexpected control character in string' in error_string:
                return unexpected_control_character_in_string(to_decode, depth)
    except HandledJSONError as e:
        return error_handler(e.fixed, e.error, depth + 1)

    if depth >= _MAXIMUM_DEPTH:
        logging.error("Tried to many attempts: %d attempts", depth)
    else:
        logging.error("Unable to fix JSON: Unknown error: %s", error)

    raise error
