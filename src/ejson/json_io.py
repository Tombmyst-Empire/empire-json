from __future__ import annotations

import csv
from contextlib import ExitStack
from typing import Any, BinaryIO, Callable, Generator, TextIO

from empire_commons.on_error import OnError, handle_error
from empire_commons.types_ import JsonList, JsonType
from openpyxl.reader.excel import load_workbook

from ejson.facades.orjson_ import dumps, json, loads


class JSON_IO:
    """
    Utility methods for IO focussed on JSON data.
    """

    @staticmethod
    def write_ndjson_to_file(
        _file: str, json_list: JsonList, *, compact: bool = True, on_error_behavior: OnError = OnError.LOG, should_append: bool = False, **kwargs
    ) -> bool:
        """
        Write *json_list* to *file_*
        :param _file: The file
        :param json_list: The json list
        :param compact: When false, pretty prints to file
        :param on_error_behavior: Behavior this function should have on error
        :param should_append: When true, appends to file instead of truncating it
        :param kwargs: Kwargs passed to :func:`ejson.facades.orjson_.dumps`
        :return: True on success
        """
        with open(_file, "a" if should_append else "w", encoding="utf8") as f:
            return JSON_IO.write_ndjson_to_opened_file(f, json_list, compact=compact, on_error_behavior=on_error_behavior)

    @staticmethod
    def write_ndjson_to_opened_file(
        _file: TextIO | BinaryIO, json_list: JsonList, *, compact: bool = True, on_error_behavior: OnError = OnError.LOG, **kwargs
    ) -> bool:
        """
        Write *json_list* to already opened *file_*
        :param _file: The file handle
        :param json_list: The json list
        :param compact: When false, pretty prints to file
        :param on_error_behavior: Behavior this function should have on error
        :param kwargs: Kwargs passed to :func:`ejson.facades.orjson_.dumps`
        :return: True on success
        """
        try:
            for record in json_list:
                _file.write(dumps(record, pretty_print_2_spaces=not compact, **kwargs) + "\n")
            return True
        except Exception as error:
            handle_error(error, on_error_behavior, message=f"An error occurred while writing ndjson data to file {_file}")
            return False

    @staticmethod
    def write_json_to_file(_file: str, _json: JsonType, *, compact: bool = True, on_error_behavior: OnError = OnError.LOG, **kwargs) -> bool:
        """
        Writes *json_* to *file_*
        :param _file: The file
        :param _json: The json
        :param compact: When false, pretty prints to file
        :param on_error_behavior: Behavior this function should have on error
        :param kwargs: Kwargs passed to :func:`ejson.facades.orjson_.dumps`
        :return: True on success
        """
        try:
            with open(_file, "w", encoding="utf8") as f:
                f.write(dumps(_json, pretty_print_2_spaces=not compact, **kwargs))
            return True
        except Exception as error:
            handle_error(error, on_error_behavior, message=f"An error occurred while writing json data to file {_file}")
            return False

    @staticmethod
    def write_json_or_ndjson_to_file(
        _file: str, data: JsonType | JsonList, *, compact: bool = True, on_error_behavior: OnError = OnError.LOG, **kwargs
    ) -> bool:
        """
        Write *data* to file. If data is a *JsonList*, it will be written as ND-JSON, otherwise it will
        be written as plain JSON

        :param _file: The file
        :param data: The data
        :param compact: When false, pretty prints to file
        :param on_error_behavior: Behavior this function should have on error
        :param kwargs: Kwargs passed to :func:`ejson.facades.orjson_.dumps`
        :return: True on success
        """
        if isinstance(data, list):
            return JSON_IO.write_ndjson_to_file(_file, data, compact=compact, on_error_behavior=on_error_behavior)

        return JSON_IO.write_json_to_file(_file, data, compact=compact, on_error_behavior=on_error_behavior)

    @staticmethod
    def read_json_from_file(
        _file: str, error_handler: Callable[[str, json.JSONDecodeError], JsonType] | None = None, on_error_behavior: OnError = OnError.LOG
    ) -> JsonType | None:
        """
        Reads JSON from *file*
        :param _file: The file
        :param error_handler: When provided, a callable that handles error that
        occurred while parsing the JSON. For example,
        see :func:`ejson.error_handler.json_error_handler.error_handler`
        :param on_error_behavior: Behavior this function should have on error
        :return: The read and parsed JSON on success, None otherwise
        """
        with open(_file, encoding="utf8") as f:
            try:
                raw: str = f.read()
                return loads(raw, error_handler)
            except Exception as error:
                handle_error(error, on_error_behavior, message=f"Cannot load JSON from file {_file}")
                return None

    @staticmethod
    def read_ndjson_from_file(
        _file: str, error_handler: Callable[[str, json.JSONDecodeError], JsonType] | None = None, on_error_behavior: OnError = OnError.LOG
    ) -> JsonList:
        """
        Reads ND-JSON from *file*
        :param _file: The file
        :param error_handler: When provided, a callable that handles error that
        occurred while parsing the JSON. For example,
        see :func:`ejson.error_handler.json_error_handler.error_handler`
        :param on_error_behavior: Behavior this function should have on error
        :return: The read and parsed *JsonList* on success, None otherwise
        """
        ndjson: JsonList = []
        with open(_file, encoding="utf8") as f:
            for index, l in enumerate(f):
                try:
                    ndjson.append(loads(l, error_handler))
                except Exception as error:
                    handle_error(error, on_error_behavior, message=f"Cannot load JSON at line {index} from file {_file}")
                    break

        return ndjson

    @staticmethod
    def _try_parse_json(data: str, on_error: OnError) -> JsonType | None:
        if not data or not data.strip():
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError as error:
            handle_error(error, on_error, message="Could not parse json from source")
            return None

    @staticmethod
    def yield_json_list_from_file(_file: str, batch_size: int, on_error_behavior: OnError = OnError.LOG) -> Generator[JsonList, Any, None]:
        """
        A generator yielding *JsonList* objects from ND-JSON *file_*.

        These lists will be of length of at most *batch_size*.

        :param _file: The ND-JSON file
        :param batch_size: The maximum size each list should be
        :param on_error_behavior: Behavior this function should have on error
        :return: Generator of *JsonList*
        """
        with ExitStack() as stack:
            provider = stack.enter_context(open(_file, "r", encoding="utf8"))

            chunk: list[JsonType] = []
            line_number: int = 0

            for line in provider:
                line_number += 1

                if (result := JSON_IO._try_parse_json(line, on_error_behavior)) is not None:
                    chunk.append(result)

                if len(chunk) >= batch_size:
                    yield chunk
                    chunk = []

            if chunk:
                yield chunk

    @staticmethod
    def yield_json_list_from_csv(_file: str, batch_size: int) -> Generator[JsonList, Any, None]:
        """
        A generator yielding *JsonList* objects from CSV *file_*.

        These lists will be of length of at most *batch_size*.

        :param _file: The CSV file
        :param batch_size: The maximum size each list should be
        :return: Generator of *JsonList*
        """
        buffer: list[JsonType] = []

        with open(_file, "r", encoding="utf8") as csv_file:
            reader = csv.DictReader(csv_file)
            for data in reader:
                data = {key: None if not value else value for (key, value) in data.items()}
                buffer.append(data)

                if len(buffer) >= batch_size:
                    yield buffer
                    buffer = []

        if buffer:
            yield buffer

    @staticmethod
    def _parse_value_from_excel(cell_value: Any) -> Any:
        if isinstance(cell_value, str):
            try:
                if cell_value.lower() in ["false", "true"]:
                    return cell_value.lower() == "true"

                if cell_value[0] in ["[", "{"] and cell_value[-1] in ["]", "}"]:
                    return json.loads(cell_value)
            except IndexError:
                return cell_value

        return cell_value

    @staticmethod
    def yield_json_list_from_excel(_file: str, batch_size: int) -> Generator[JsonList, Any, None]:
        """
        A generator yielding *JsonList* objects from an Excel *file_*.

        These lists will be of length of at most *batch_size*.

        :param _file: The Excel file
        :param batch_size: The maximum size each list should be
        :return: Generator of *JsonList*
        """

        # I could have used pandas, but I did not find a proper way to read excel files as generators...
        excel_file = load_workbook(
            filename=_file,
            read_only=True,
            keep_vba=False,
            data_only=True,
            keep_links=False,
        )

        first_row: Any = next(excel_file.worksheets[0].rows)
        field_names: tuple[str, ...] = tuple(str(cell.value) for cell in first_row if cell.value)

        buffer: list[JsonType] = []

        for index, row in enumerate(excel_file.worksheets[0].rows):
            if index == 0:  # skip header row that contains field names
                continue

            cells: list[str] = [cell.value for cell in row]

            if not any(cells):
                continue

            cells = [JSON_IO._parse_value_from_excel(cell) if cell else None for cell in cells]
            buffer.append(dict(zip(field_names, cells)))

            if len(buffer) >= batch_size:
                yield buffer
                buffer = []

        if buffer:
            yield buffer


YIELDER_MAP_BY_EXTENSION = {  #: A mapping of file extensions to corresponding generator method
    "ndjson": JSON_IO.yield_json_list_from_file,
    "nl": JSON_IO.yield_json_list_from_file,
    "jsonl": JSON_IO.yield_json_list_from_file,
    "csv": JSON_IO.yield_json_list_from_csv,
    "xlsx": JSON_IO.yield_json_list_from_excel,
    "xls": JSON_IO.yield_json_list_from_excel,
}

YIELDER_MAP_BY_FILE_TYPE = {  #: A mapping of file types to corresponding generator method
    "ndjson": JSON_IO.yield_json_list_from_file,
    "csv": JSON_IO.yield_json_list_from_csv,
    "excel": JSON_IO.yield_json_list_from_excel,
}
