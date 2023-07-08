import ast
import logging
from contextlib import suppress
from typing import Any, Callable, Optional

import rapidjson as json

from empire_commons.types_ import NULL, JsonType
from ejson.error_handler.handled_json_error import HandledJSONError
from ejson.error_handler.regexes import (
    NON_DOUBLE_QUOTED_KEY_REGEX,
    NON_ESCAPED_DOUBLE_QUOTE,
    OFFSET_EXTRACTOR,
    SINGLE_QUOTED_VALUE_REGEX, CONTROL_CHARACTERS,
)


def try_fix(
    attempt_message: str, fix: Callable[[str], str], to_decode: str, depth: int
) -> JsonType | tuple[Optional[str], json.JSONDecodeError]:
    logging.info(attempt_message)
    fixed: Optional[str] = None
    try:
        fixed = fix(to_decode)
        attempt: Any = json.loads(fixed)
        logging.success("Successfully fixed JSON!")  # pylint: disable=no-member
        return attempt
    except json.JSONDecodeError as error:
        raise HandledJSONError(fixed, error)


def fix_non_double_quoted_strings(to_decode: str) -> str:
    return NON_DOUBLE_QUOTED_KEY_REGEX.sub(r'"\1"', to_decode)


def fix_string_values_single_quoted(to_decode: str) -> str:
    return SINGLE_QUOTED_VALUE_REGEX.sub(r'"\1"', to_decode)


def fix_non_escaped_double_quotes(to_decode: str) -> str:
    return NON_ESCAPED_DOUBLE_QUOTE.sub(r"\1\"\2", to_decode)


def fix_double_double_quotes(to_decode: str) -> str:
    return to_decode.replace('""', '"')


def fix_unescaped_control_characters(to_decode: str) -> str:
    return CONTROL_CHARACTERS.sub(' ', to_decode)


def try_parse_repr_json(to_decode: str) -> Any:
    with suppress(Exception):
        attempt: Any = ast.literal_eval(to_decode)
        logging.success(
            "Provided JSON was a repr() string"
        )  # pylint: disable=no-member
        return attempt

    return NULL
