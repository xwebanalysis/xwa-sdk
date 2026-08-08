"""Validation helpers backed by the canonical JSON Schemas."""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

_SCHEMA_DIR = Path(__file__).parent / "schemas"
_VALIDATORS: dict[str, Draft202012Validator] = {}


def _schema_path(name: str) -> Path:
    path = _SCHEMA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Schema not bundled: {path}")
    return path


def _load(name: str) -> Draft202012Validator:
    if name not in _VALIDATORS:
        data = json.loads(_schema_path(name).read_text(encoding="utf-8"))
        _VALIDATORS[name] = Draft202012Validator(data)
    return _VALIDATORS[name]


def validate_analysis(data: dict) -> None:
    """Raise ValidationError if data is not a valid Analysis."""
    _load("analysis.json").validate(data)


def validate_finding(data: dict) -> None:
    """Raise ValidationError if data is not a valid Finding."""
    _load("finding.json").validate(data)


def validate_event(data: dict) -> None:
    """Raise ValidationError if data is not a valid Event."""
    _load("event.json").validate(data)


def validate_error(data: dict) -> None:
    """Raise ValidationError if data is not a valid Error."""
    _load("error.json").validate(data)


def validate_item(kind: str, data: dict) -> None:
    """Validate a module item by schema name, e.g. 'link', 'technology'."""
    _load(f"items/{kind}.json").validate(data)


def is_valid_analysis(data: dict) -> bool:
    try:
        validate_analysis(data)
        return True
    except ValidationError:
        return False


def is_valid_finding(data: dict) -> bool:
    try:
        validate_finding(data)
        return True
    except ValidationError:
        return False


def is_valid_event(data: dict) -> bool:
    try:
        validate_event(data)
        return True
    except ValidationError:
        return False


__all__ = [
    "ValidationError",
    "validate_analysis",
    "validate_finding",
    "validate_event",
    "validate_error",
    "validate_item",
    "is_valid_analysis",
    "is_valid_finding",
    "is_valid_event",
]
