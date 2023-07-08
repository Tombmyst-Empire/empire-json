from typing import Final

import regex as re

OFFSET_EXTRACTOR: Final[re.Pattern] = re.compile(r"offset (\d+):")
OFFSET_EXTRACTOR_CHAR_VARIANT: Final[re.Pattern] = re.compile("\(char (\d+)\)")
NON_DOUBLE_QUOTED_KEY_REGEX: Final[re.Pattern] = re.compile(
    r"(?<=[{, ])'?([^'\"]+)'?(?=:[ \"'])"
)
SINGLE_QUOTED_VALUE_REGEX: Final[re.Pattern] = re.compile(
    r"(?<=: |:|\[)'([^']*)'(?=[,} \]])"
)
NON_ESCAPED_DOUBLE_QUOTE: Final[re.Pattern] = re.compile(
    r"(?<=[{: ,])(\"[^'\"]*)\"([^'\"]*\")(?=[,}: ])"
)
CONTROL_CHARACTERS: Final[re.Pattern] = re.compile(r"(\n|\r|\t|\f|\v|\a)")