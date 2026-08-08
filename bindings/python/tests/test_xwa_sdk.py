"""Tests for xwa_sdk models and schema validation."""

import pytest

from xwa_sdk import (
    Analysis,
    Error,
    Event,
    Finding,
    Summary,
    from_dict,
    map_severity,
    to_dict,
    validate_analysis,
    validate_event,
    validate_finding,
    validate_item,
)
from xwa_sdk.models import DiscoveredLink, Technology
from xwa_sdk.validation import ValidationError


def sample_analysis() -> dict:
    return {
        "id": "scan-42",
        "tool": "samurai",
        "target": "https://example.com",
        "status": "RUNNING",
        "created_at": "2026-08-08T10:00:00Z",
        "analysis_type": "port_scan",
        "summary": {"total_items": 3, "by_severity": {"high": 1, "info": 2}, "by_category": {}},
    }


def test_analysis_roundtrip():
    data = sample_analysis()
    analysis = from_dict(Analysis, data)
    assert analysis.id == "scan-42"
    assert analysis.tool == "samurai"
    assert analysis.summary.total_items == 3
    assert to_dict(analysis) == data


def test_analysis_validation_ok():
    validate_analysis(sample_analysis())


def test_analysis_validation_fails_on_bad_status():
    data = sample_analysis()
    data["status"] = "PAUSED"
    with pytest.raises(ValidationError):
        validate_analysis(data)


def test_finding_validation():
    validate_finding({
        "tool": "tengu",
        "severity": "medium",
        "title": "Missing alt text",
        "description": "Image lacks alternative text",
        "category": "a11y",
        "target_url": "https://example.com/img.png",
    })


def test_finding_invalid_severity():
    with pytest.raises(ValidationError):
        validate_finding({
            "tool": "tengu",
            "severity": "urgent",
            "title": "x",
            "description": "y",
        })


def test_event_validation():
    validate_event({
        "seq": 1,
        "type": "item_found",
        "tool": "kensei",
        "analysis_id": "profile-1",
        "ts": "2026-08-08T10:00:01Z",
        "payload": {"category": "frontend", "name": "Angular"},
    })


def test_module_items():
    validate_item("link", {"url": "https://example.com/a", "status_code": 200})
    validate_item("technology", {"category": "cdn", "name": "Cloudflare"})
    with pytest.raises(ValidationError):
        validate_item("technology", {"name": "missing category"})


def test_severity_mapping():
    assert map_severity("tengu", "Pass") == "pass"
    assert map_severity("tengu", "Warning") == "medium"
    assert map_severity("tengu", "Error") == "high"
    assert map_severity("samurai", "critical") == "critical"
    with pytest.raises(ValueError):
        map_severity("samurai", "Warning")


def test_error_model():
    err = Error(code="TIMEOUT", message="Target did not respond", retryable=True)
    analysis = Analysis(
        id="a1", tool="shinobi", target="https://x.com", status="ERROR",
        created_at="2026-08-08T10:00:00Z", error=err,
    )
    data = to_dict(analysis)
    restored = from_dict(Analysis, data)
    assert restored.error.code == "TIMEOUT"
    assert restored.error.retryable is True


def test_event_from_dict_with_payload():
    ev = from_dict(Event, {
        "seq": 2,
        "type": "log",
        "tool": "tengu",
        "analysis_id": "audit-7",
        "ts": "2026-08-08T10:00:02Z",
        "payload": {"message": "crawling"},
    })
    assert ev.payload["message"] == "crawling"


def test_samurai_finding_with_poc():
    f = Finding(
        tool="samurai", severity="high", title="SQLi", description="Blind SQLi",
        category="sqli", evidence={"poc_payload": "' OR 1=1--"},
        cvss_score="9.8",
    )
    data = to_dict(f)
    validate_finding(data)
    assert map_severity("samurai", data["severity"]) == "high"
