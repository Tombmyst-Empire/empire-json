from ejson.error_handler.regexes import (
    NON_DOUBLE_QUOTED_KEY_REGEX,
    NON_ESCAPED_DOUBLE_QUOTE,
    SINGLE_QUOTED_VALUE_REGEX,
)


def there_are_keys_non_double_quoted(to_decode: str) -> bool:
    return bool(NON_DOUBLE_QUOTED_KEY_REGEX.search(to_decode))


def there_string_values_single_quoted(to_decode: str) -> bool:
    return bool(SINGLE_QUOTED_VALUE_REGEX.search(to_decode))


def there_are_non_escaped_double_quotes(to_decode: str) -> bool:
    return bool(NON_ESCAPED_DOUBLE_QUOTE.search(to_decode))


def there_are_double_double_quotes(to_decode: str) -> bool:
    return '""' in to_decode
