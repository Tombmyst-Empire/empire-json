from typing import Any


class HandledJSONError(Exception):
    def __init__(self, fixed: str, error: Any):
        self.fixed: str = fixed
        self.error: Any = error
        super().__init__("HandledJSONError")
