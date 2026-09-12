"""Validation helpers backed by the canonical JSON Schemas.

The canonical schemas live in ``xwa-sdk/schemas/`` and are bundled 1:1 inside
this package (``xwa_sdk/schemas/``, kept in sync by ``scripts/sync_schemas.py``).
Validation is fully offline: a local :class:`referencing.Registry` maps every
bundled ``$id`` URI, so relative ``$ref`` targets (for example
``analysis.json`` -> ``error.json``) resolve without network access.

All ``validate_*`` helpers raise :class:`jsonschema.exceptions.ValidationError`
on invalid payloads — never a referencing error. ``is_valid_*`` predicates
return a plain ``bool`` and never raise for reference-resolution problems.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

_SCHEMA_DIR = Path(__file__).parent / "schemas"
_VALIDATORS: dict[str, Draft202012Validator] = {}
_REGISTRY: Registry | None = None

#: Item schema names accepted by :func:`validate_item` (``items/<kind>.json``).
ITEM_KINDS = (
    "link",
    "technology",
    "route",
    "dependency",
    "waf",
    "cdn",
    "challenge",
    "rate_limit",
    "api_endpoint",
)


def _schema_path(name: str) -> Path:
    path = _SCHEMA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Schema not bundled: {path}")
    return path


def _registry() -> Registry:
    """Build (once) a registry containing every bundled schema by ``$id``.

    Both remote ``$id`` values (e.g. ``https://…/schemas/analysis.json``) and
    relative ``$ref`` targets (``error.json`` resolved against the referring
    schema's base URI) are served from this local registry.
    """
    global _REGISTRY
    if _REGISTRY is None:
        resources: list[tuple[str, Resource]] = []
        for path in sorted(_SCHEMA_DIR.rglob("*.json")):
            contents = json.loads(path.read_text(encoding="utf-8"))
            resource = Resource.from_contents(
                contents, default_specification=DRAFT202012
            )
            uri = contents.get("$id") or path.as_uri()
            resources.append((uri, resource))
        _REGISTRY = Registry().with_resources(resources)
    return _REGISTRY


def _load(name: str) -> Draft202012Validator:
    if name not in _VALIDATORS:
        data = json.loads(_schema_path(name).read_text(encoding="utf-8"))
        _VALIDATORS[name] = Draft202012Validator(data, registry=_registry())
    return _VALIDATORS[name]


def _validate(name: str, data: Any) -> None:
    """Validate *data* against a bundled schema, normalizing reference errors."""
    try:
        _load(name).validate(data)
    except Unresolvable as exc:  # pragma: no cover - all refs are bundled
        # Defensive: if a bundled $ref still cannot be resolved, surface it as
        # a regular ValidationError so callers only handle one exception type.
        raise ValidationError(
            f"Unresolvable schema reference while validating {name}: {exc}"
        ) from exc


def validate_analysis(data: dict) -> None:
    """Raise ValidationError if data is not a valid Analysis."""
    _validate("analysis.json", data)


def validate_finding(data: dict) -> None:
    """Raise ValidationError if data is not a valid Finding."""
    _validate("finding.json", data)


def validate_event(data: dict) -> None:
    """Raise ValidationError if data is not a valid Event."""
    _validate("event.json", data)


def validate_error(data: dict) -> None:
    """Raise ValidationError if data is not a valid Error."""
    _validate("error.json", data)


def validate_item(kind: str, data: dict) -> None:
    """Validate a module item by schema name, e.g. 'link', 'technology'."""
    _validate(f"items/{kind}.json", data)


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


def is_valid_error(data: dict) -> bool:
    try:
        validate_error(data)
        return True
    except ValidationError:
        return False


def is_valid_item(kind: str, data: dict) -> bool:
    try:
        validate_item(kind, data)
        return True
    except ValidationError:
        return False


__all__ = [
    "ITEM_KINDS",
    "ValidationError",
    "validate_analysis",
    "validate_finding",
    "validate_event",
    "validate_error",
    "validate_item",
    "is_valid_analysis",
    "is_valid_finding",
    "is_valid_event",
    "is_valid_error",
    "is_valid_item",
]
