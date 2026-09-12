"""Offline validation and nullable-enum regression tests (0.2.0).

Covers:
- nested ``$ref`` (``analysis.json`` -> ``error.json``) resolved from the
  bundled schemas with a local ``referencing.Registry`` (no network);
- ``validate_*`` raising plain :class:`jsonschema.ValidationError`;
- ``is_valid_*`` returning a bool instead of leaking referencing errors;
- optional enum fields accepting ``null`` and a valid value, rejecting bogus.
"""

from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

import xwa_sdk.validation as validation
from xwa_sdk import (
    is_valid_analysis,
    is_valid_error,
    is_valid_finding,
    is_valid_item,
    validate_analysis,
    validate_error,
    validate_finding,
    validate_item,
)


def analysis_with_error() -> dict:
    return {
        "id": "scan-42",
        "tool": "samurai",
        "target": "https://example.com",
        "status": "ERROR",
        "created_at": "2026-08-08T10:00:00Z",
        "started_at": "2026-08-08T10:00:01Z",
        "finished_at": "2026-08-08T10:00:05Z",
        "error": {
            "code": "NETWORK_ERROR",
            "message": "Target did not respond",
            "detail": {"phase": "connect", "retries": 3},
            "retryable": True,
        },
    }


def test_analysis_with_nested_error_validates_offline():
    validate_analysis(analysis_with_error())


def test_analysis_with_nested_error_is_valid_offline():
    assert is_valid_analysis(analysis_with_error()) is True


def test_invalid_nested_error_raises_plain_validation_error():
    data = analysis_with_error()
    data["error"] = {"message": "missing code"}
    with pytest.raises(ValidationError):
        validate_analysis(data)
    assert is_valid_analysis(data) is False


def test_validate_error_directly():
    validate_error({"code": "TIMEOUT", "message": "no response"})
    with pytest.raises(ValidationError):
        validate_error({"message": "missing code"})
    assert is_valid_error({"code": "TIMEOUT", "message": "no response"})
    assert is_valid_error({"message": "missing code"}) is False


def test_is_valid_does_not_propagate_referencing_errors(monkeypatch):
    """If a $ref cannot be resolved, predicates must return False, not raise."""
    schema = validation._schema_path("analysis.json").read_text(encoding="utf-8")
    import json

    bare = Draft202012Validator(json.loads(schema))  # no registry
    monkeypatch.setitem(validation._VALIDATORS, "analysis.json", bare)
    assert is_valid_analysis(analysis_with_error()) is False
    # validate_* still raises ValidationError, never the raw referencing error.
    with pytest.raises(ValidationError):
        validate_analysis(analysis_with_error())


# ── Nullable optional enums ────────────────────────────────────────────────

NULLABLE_ENUM_CASES = [
    (
        "finding",
        lambda value: validate_finding(
            {
                "tool": "samurai",
                "severity": "high",
                "title": "t",
                "description": "d",
                "confidence": value,
            }
        ),
    ),
    (
        "technology",
        lambda value: validate_item("technology", {"category": "cdn", "name": "CF", "confidence": value}),
    ),
    (
        "route.framework",
        lambda value: validate_item("route", {"path": "/a", "framework": value}),
    ),
    (
        "route.route_type",
        lambda value: validate_item("route", {"path": "/a", "route_type": value}),
    ),
    (
        "dependency.source",
        lambda value: validate_item("dependency", {"name": "rxjs", "source": value}),
    ),
    (
        "dependency.package_manager",
        lambda value: validate_item("dependency", {"name": "rxjs", "package_manager": value}),
    ),
]


@pytest.mark.parametrize("label,run", NULLABLE_ENUM_CASES, ids=[c[0] for c in NULLABLE_ENUM_CASES])
def test_nullable_enum_accepts_null(label, run):
    run(None)  # must not raise


@pytest.mark.parametrize("label,run", NULLABLE_ENUM_CASES, ids=[c[0] for c in NULLABLE_ENUM_CASES])
def test_nullable_enum_rejects_bogus(label, run):
    with pytest.raises(ValidationError):
        run("bogus")


def test_nullable_enum_accepts_valid_values():
    validate_finding(
        {
            "tool": "tengu",
            "severity": "medium",
            "title": "t",
            "description": "d",
            "confidence": "high",
        }
    )
    validate_item("technology", {"category": "backend", "name": "Django", "confidence": "low"})
    validate_item("route", {"path": "/a", "framework": "angular", "route_type": "lazy"})
    validate_item("dependency", {"name": "rxjs", "source": "bundle", "package_manager": "npm"})


def test_is_valid_item_false_on_bogus_enum():
    assert is_valid_item("technology", {"category": "cdn", "name": "CF", "confidence": None}) is True
    assert is_valid_item("technology", {"category": "cdn", "name": "CF", "confidence": "bogus"}) is False
