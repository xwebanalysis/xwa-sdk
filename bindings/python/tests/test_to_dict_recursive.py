"""Recursive ``to_dict`` / ``from_dict`` roundtrip tests (0.2.0)."""

from __future__ import annotations

from xwa_sdk import (
    Analysis,
    ApiEndpoint,
    Cdn,
    Challenge,
    Error,
    Event,
    Finding,
    RateLimit,
    Summary,
    Technology,
    Waf,
    from_dict,
    to_dict,
)


def test_to_dict_omits_top_level_none():
    finding = Finding(tool="tengu", severity="info", title="t", description="d")
    data = to_dict(finding)
    assert "id" not in data
    assert "category" not in data
    assert "confidence" not in data
    assert data == {"tool": "tengu", "severity": "info", "title": "t", "description": "d"}


def test_to_dict_omits_nested_none_from_dataclasses():
    analysis = Analysis(
        id="a1",
        tool="samurai",
        target="https://example.com",
        status="ERROR",
        created_at="2026-08-08T10:00:00Z",
        error=Error(code="TIMEOUT", message="no response", detail=None),
        summary=Summary(total_items=None, by_severity={}, by_category={}),
    )
    data = to_dict(analysis)
    assert data["error"] == {"code": "TIMEOUT", "message": "no response", "retryable": False}
    assert "detail" not in data["error"]
    assert data["summary"] == {"by_severity": {}, "by_category": {}}
    assert "total_items" not in data["summary"]


def test_to_dict_omits_none_inside_plain_dicts_and_lists():
    finding = Finding(
        tool="samurai",
        severity="high",
        title="t",
        description="d",
        evidence={
            "snippet": "<script>",
            "poc_payload": None,
            "data": {"nested": None, "keep": {"deep": None, "deeper": 1}},
            "list": [{"a": None, "b": 2}, None, 3],
        },
    )
    data = to_dict(finding)
    assert data["evidence"] == {
        "snippet": "<script>",
        "data": {"keep": {"deeper": 1}},
        "list": [{"b": 2}, 3],
    }


def test_to_dict_accepts_plain_structures():
    assert to_dict({"a": None, "b": {"c": None, "d": 1}}) == {"b": {"d": 1}}
    assert to_dict([None, {"x": None, "y": 2}]) == [{"y": 2}]


ROUNDTRIP_MODELS = [
    Analysis(
        id="a1",
        tool="kabuki",
        target="https://example.com",
        status="COMPLETED",
        created_at="2026-08-08T10:00:00Z",
        tool_version="0.2.0",
        analysis_type="waf_profile",
        error=None,
        summary=Summary(total_items=1, by_severity={"info": 1}, by_category={}),
    ),
    Finding(
        tool="tengu",
        severity="medium",
        title="t",
        description="d",
        evidence={"snippet": "x"},
        confidence=None,
        cvss_score=None,
    ),
    Event(seq=1, type="log", tool="tengu", analysis_id="a1", ts="2026-08-08T10:00:01Z", payload=None),
    Waf(vendor="Cloudflare", product=None, confidence="high", blocked=True, severity="info"),
    Cdn(provider="Fastly", edge_nodes=["FRA"], origin_hidden=True, caching=None),
    Challenge(kind="captcha", status_code=403, headers={"cf-mitigated": "challenge"}),
    RateLimit(scope="ip", limit=100, window_seconds=60, recommended_delay_ms=None),
    ApiEndpoint(
        protocol="rest",
        path="/v1/users",
        method="GET",
        params=[{"name": "page", "location": "query", "type": "integer"}],
        auth_required=True,
        source="openapi",
    ),
]


def test_roundtrip_all_models_strips_none_and_rebuilds_equal():
    for model in ROUNDTRIP_MODELS:
        payload = to_dict(model)
        assert _has_no_none(payload), f"{type(model).__name__} still has None: {payload!r}"
        restored = from_dict(type(model), payload)
        assert restored == model, f"{type(model).__name__} roundtrip mismatch"


def test_roundtrip_normalizes_none_inside_user_dicts():
    """None entries inside user payloads are dropped and do not come back."""
    finding = Finding(
        tool="samurai",
        severity="high",
        title="t",
        description="d",
        evidence={"snippet": "x", "poc_payload": None, "data": {"deep": None, "keep": 1}},
    )
    payload = to_dict(finding)
    assert payload["evidence"] == {"snippet": "x", "data": {"keep": 1}}
    restored = from_dict(Finding, payload)
    assert restored.evidence == {"snippet": "x", "data": {"keep": 1}}


def _has_no_none(value) -> bool:
    if isinstance(value, dict):
        return all(_has_no_none(v) for v in value.values())
    if isinstance(value, list):
        return all(_has_no_none(v) for v in value)
    return value is not None
