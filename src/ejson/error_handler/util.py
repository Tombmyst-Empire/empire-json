from contextlib import suppress
from typing import Optional

from empire_commons.list_util import try_get
from ejson.error_handler.regexes import OFFSET_EXTRACTOR, OFFSET_EXTRACTOR_CHAR_VARIANT


def get_offset_from_error_string(error_string: str) -> Optional[int]:
    offset: str = try_get(OFFSET_EXTRACTOR.findall(error_string), 0)
    with suppress(TypeError):
        return int(offset)
    offset: str = try_get(OFFSET_EXTRACTOR_CHAR_VARIANT.findall(error_string), 0)
    with suppress(TypeError):
        return int(offset)

    return None
