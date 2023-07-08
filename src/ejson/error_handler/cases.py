import logging
from typing import Optional

from empire_commons.types_ import NULL
from ejson.error_handler.evaluators import (
    there_are_double_double_quotes,
    there_are_keys_non_double_quoted,
    there_are_non_escaped_double_quotes,
    there_string_values_single_quoted,
)
from ejson.error_handler.fixers import (
    fix_double_double_quotes,
    fix_non_double_quoted_strings,
    fix_non_escaped_double_quotes,
    fix_string_values_single_quoted,
    try_fix,
    try_parse_repr_json, fix_unescaped_control_characters,
)
from ejson.error_handler.util import get_offset_from_error_string


def missing_name_for_object_member(to_decode: str, depth: int) -> Optional[str]:
    logging.info(
        "Unable to decode JSON string: Missing a name for object member (it cannot interpret a key)"
    )
    attempt = try_parse_repr_json(to_decode)
    if attempt != NULL:
        return attempt

    if there_are_keys_non_double_quoted(to_decode):
        return try_fix(
            "There are keys that are not surrounded by double quotes, attempting to fix...",
            fix_non_double_quoted_strings,
            to_decode,
            depth,
        )


def invalid_value(to_decode: str, depth: int) -> Optional[str]:
    logging.info(
        "Unable to decode JSON string: Invalid value (it cannot interpret a value)"
    )
    attempt = try_parse_repr_json(to_decode)
    if attempt != NULL:
        return attempt

    if there_string_values_single_quoted(to_decode):
        return try_fix(
            "There are string values that are surrounded by single quotes (should be double quotes)",
            fix_string_values_single_quoted,
            to_decode,
            depth,
        )


def unexpected_control_character_in_string(to_decode: str, depth: int) -> Optional[str]:
    logging.info('Probably from ORJSON only: "unexpected control character in string". This can be a \\n or stuff like that')
    return try_fix(
        "Attempting to fix by escaping all control characters",
        fix_unescaped_control_characters,
        to_decode,
        depth,
    )


def missing_comma_or_curly_bracket_after_object_member(
    to_decode, depth: int
) -> Optional[str]:
    logging.info(
        "Unable to decode JSON string: Missing a comma or '}' after an object member (probably a non-escaped double quote in a value)"
    )
    if there_are_double_double_quotes(to_decode):
        return try_fix(
            'There are consecutive double quotes ("")',
            fix_double_double_quotes,
            to_decode,
            depth,
        )
    if there_are_non_escaped_double_quotes(to_decode):
        return try_fix(
            "There are non escaped double quotes",
            fix_non_escaped_double_quotes,
            to_decode,
            depth,
        )
