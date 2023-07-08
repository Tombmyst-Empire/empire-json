from __future__ import annotations

from empire_commons.types_ import JsonList, JsonType


class JSONList:
    """
    Utilities for list of JSONs (or dictionaries)
    """

    @staticmethod
    def map_by_field(
        field_name: str, json_list: JsonList, ignore_when_field_is_missing: bool = False, remove_field_from_mapped_json: bool = False
    ) -> JsonType:
        """
        From the provided *json_list*, this method creates a JSON object that refers every
        list's records by the specified *field_name* value in these items.

        :param field_name: The field name to use to create the result.
        :param json_list: The list of JSON objects
        :param ignore_when_field_is_missing: When True, ignores any list's record that does
            not contain *field_name*: it does not add this record to the result.
        :param remove_field_from_mapped_json: When True, *field_name* is deleted from
            the resulting JSON object
        :return: A JSON object
        """
        result: JsonType = {}

        for record in json_list:
            try:
                result[record[field_name]] = record
                if remove_field_from_mapped_json:
                    del result[record[field_name]][field_name]
            except KeyError:
                if not ignore_when_field_is_missing:
                    raise

        return result
