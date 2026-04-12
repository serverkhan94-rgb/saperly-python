from __future__ import annotations

import re


def _camel_to_snake(s: str) -> str:
    # Two-pass: handles acronyms like HTTPStatus -> http_status, callSID -> call_sid
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def to_snake_keys(obj: object) -> object:
    """Recursively convert all dict keys from camelCase to snake_case."""
    if isinstance(obj, dict):
        return {_camel_to_snake(k): to_snake_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_snake_keys(item) for item in obj]
    return obj
