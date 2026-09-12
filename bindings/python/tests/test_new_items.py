"""Validation and model tests for the new kabuki/yari item schemas (0.2.0)."""

from __future__ import annotations

import pytest
from jsonschema.exceptions import ValidationError

from xwa_sdk import (
    ApiEndpoint,
    Cdn,
    Challenge,
    RateLimit,
    Waf,
    from_dict,
    to_dict,
    validate_item,
)
from xwa_sdk.validation import ITEM_KINDS, is_valid_item

NEW_ITEM_KINDS = ("waf", "cdn", "challenge", "rate_limit", "api_endpoint")


def test_item_kinds_exposed():
    for kind in NEW_ITEM_KINDS:
        assert kind in ITEM_KINDS


VALID_ITEMS = [
    ("waf", {"vendor": "Cloudflare"}),
    (
        "waf",
        {
            "vendor": "AWS",
            "product": "WAF",
            "confidence": "high",
            "detection_method": "header",
            "evidence": "x-amzn-waf-action",
            "blocked": True,
            "severity": "medium",
        },
    ),
    ("cdn", {"provider": "Fastly", "edge_nodes": ["FRA", "AMS"], "origin_hidden": True, "caching": "hit"}),
    ("challenge", {"kind": "js_challenge", "status_code": 503, "headers": {"server": "cloudflare"}}),
    ("challenge", {"kind": "captcha", "response_time_ms": 1234.5, "severity_hint": "low"}),
    ("rate_limit", {"scope": "ip", "limit": 120, "window_seconds": 60, "recommended_delay_ms": 500}),
    ("api_endpoint", {"protocol": "graphql", "path": "/graphql", "source": "graphql_introspection"}),
    (
        "api_endpoint",
        {
            "protocol": "rest",
            "path": "/v1/users",
            "method": "POST",
            "host": "api.example.com",
            "params": [{"name": "body", "location": "body", "type": "object", "required": True}],
            "auth_required": True,
            "content_types": ["application/json"],
            "version": "v1",
        },
    ),
]


@pytest.mark.parametrize("kind,payload", VALID_ITEMS, ids=[f"{k}-{i}" for i, (k, _) in enumerate(VALID_ITEMS)])
def test_new_items_validate(kind, payload):
    validate_item(kind, payload)
    assert is_valid_item(kind, payload) is True


NULLABLE_FIELDS = [
    ("waf", {"vendor": "X", "confidence": None, "detection_method": None, "evidence": None, "severity": None}),
    ("cdn", {"provider": "X", "edge_nodes": None, "caching": None, "evidence": None}),
    ("challenge", {"kind": "block_page", "status_code": None, "headers": None, "bypass_indicators": None, "response_time_ms": None, "severity_hint": None}),
    ("rate_limit", {"scope": "session", "limit": None, "window_seconds": None, "headers": None, "threshold_estimate": None, "recommended_delay_ms": None}),
    ("api_endpoint", {"protocol": "grpc", "path": "/pkg.Svc/Method", "method": None, "host": None, "params": None, "auth_required": None, "source": None, "content_types": None, "version": None}),
]


@pytest.mark.parametrize("kind,payload", NULLABLE_FIELDS, ids=[k for k, _ in NULLABLE_FIELDS])
def test_new_item_null_optional_fields_validate(kind, payload):
    validate_item(kind, payload)


MISSING_REQUIRED = [
    ("waf", {"product": "WAF"}),
    ("cdn", {"edge_nodes": ["FRA"]}),
    ("challenge", {"status_code": 403}),
    ("rate_limit", {"limit": 100}),
    ("api_endpoint", {"path": "/a"}),
    ("api_endpoint", {"protocol": "rest"}),
]


@pytest.mark.parametrize("kind,payload", MISSING_REQUIRED, ids=[f"{k}-{i}" for i, (k, _) in enumerate(MISSING_REQUIRED)])
def test_new_item_missing_required_rejected(kind, payload):
    with pytest.raises(ValidationError):
        validate_item(kind, payload)
    assert is_valid_item(kind, payload) is False


BAD_ENUMS = [
    ("waf", {"vendor": "X", "confidence": "certain"}),
    ("waf", {"vendor": "X", "detection_method": "vibes"}),
    ("waf", {"vendor": "X", "severity": "urgent"}),
    ("cdn", {"provider": "X", "caching": "sometimes"}),
    ("challenge", {"kind": "quiz"}),
    ("challenge", {"kind": "captcha", "severity_hint": "urgent"}),
    ("rate_limit", {"scope": "galaxy"}),
    ("api_endpoint", {"protocol": "soap", "path": "/a"}),
    ("api_endpoint", {"protocol": "rest", "path": "/a", "source": "guessing"}),
]


@pytest.mark.parametrize("kind,payload", BAD_ENUMS, ids=[f"{k}-{i}" for i, (k, _) in enumerate(BAD_ENUMS)])
def test_new_item_bad_enum_rejected(kind, payload):
    with pytest.raises(ValidationError):
        validate_item(kind, payload)


def test_new_item_models_roundtrip_and_validate():
    models = [
        Waf(vendor="Cloudflare", confidence="high", detection_method="header", blocked=True, severity="info"),
        Cdn(provider="CloudFront", edge_nodes=["FRA2"], origin_hidden=True, caching="stale"),
        Challenge(kind="interstitial", status_code=200, headers={"set-cookie": "x"}, bypass_indicators=["no-op"], response_time_ms=250.0, severity_hint="low"),
        RateLimit(scope="global", limit=1000, window_seconds=3600, headers={"x-ratelimit-limit": "1000"}, threshold_estimate=950, recommended_delay_ms=250),
        ApiEndpoint(protocol="rest", path="/v2/items", method="GET", host="api.example.com", params=[{"name": "q", "location": "query", "type": "string", "required": False}], auth_required=True, source="openapi", content_types=["application/json"], version="v2"),
    ]
    for model in models:
        payload = to_dict(model)
        kind = type(model).__name__.lower()
        kind = {"waf": "waf", "cdn": "cdn", "challenge": "challenge", "ratelimit": "rate_limit", "apiendpoint": "api_endpoint"}[kind]
        validate_item(kind, payload)
        assert from_dict(type(model), payload) == model
