//! Serde roundtrip and enum tests for the Rust binding (mirrors the Python tests).

use serde_json::json;
use xwa_sdk::{
    map_severity, Analysis, AnalysisStatus, ApiEndpoint, Caching, Cdn, Challenge, ChallengeKind,
    Confidence, DetectionMethod, DiscoveredLink, DiscoverySource, Error, Event, EventType, Finding,
    JsDependency, Protocol, RateLimit, RateLimitScope, Severity, Summary, Technology, Tool, Waf,
};

fn sample_analysis() -> Analysis {
    Analysis {
        id: "scan-42".into(),
        tool: Tool::Samurai,
        target: "https://example.com".into(),
        status: AnalysisStatus::Error,
        created_at: "2026-08-08T10:00:00Z".into(),
        tool_version: Some("0.2.0".into()),
        analysis_type: Some("port_scan".into()),
        started_at: Some("2026-08-08T10:00:01Z".into()),
        finished_at: Some("2026-08-08T10:00:05Z".into()),
        error: Some(Error {
            code: "NETWORK_ERROR".into(),
            message: "Target did not respond".into(),
            detail: Some(json!({"phase": "connect", "retries": 3})),
            retryable: true,
        }),
        summary: Some(Summary {
            total_items: Some(3),
            by_severity: [("high".to_string(), 1)].into_iter().collect(),
            by_category: Default::default(),
        }),
    }
}

#[test]
fn analysis_roundtrip_with_nested_error() {
    let analysis = sample_analysis();
    let json = serde_json::to_string(&analysis).unwrap();
    let restored: Analysis = serde_json::from_str(&json).unwrap();
    assert_eq!(analysis, restored);
    // Nested error is a real object, not a stale $ref string.
    let value: serde_json::Value = serde_json::from_str(&json).unwrap();
    assert_eq!(value["error"]["code"], "NETWORK_ERROR");
}

#[test]
fn optional_fields_are_skipped_when_none() {
    let finding = Finding {
        tool: Tool::Tengu,
        severity: Severity::Info,
        title: "t".into(),
        description: "d".into(),
        id: None,
        category: None,
        check: None,
        target_url: None,
        evidence: None,
        cvss_score: None,
        confidence: None,
        detected_at: None,
    };
    let value = serde_json::to_value(&finding).unwrap();
    for key in [
        "id",
        "category",
        "check",
        "target_url",
        "evidence",
        "cvss_score",
        "confidence",
        "detected_at",
    ] {
        assert!(value.get(key).is_none(), "{key} should be omitted");
    }
    assert_eq!(value["tool"], "tengu");
    assert_eq!(value["severity"], "info");
}

#[test]
fn explicit_null_deserializes_to_none() {
    let finding: Finding = serde_json::from_value(json!({
        "tool": "samurai",
        "severity": "high",
        "title": "t",
        "description": "d",
        "confidence": null,
        "id": null,
    }))
    .unwrap();
    assert_eq!(finding.confidence, None);
    assert_eq!(finding.id, None);
}

#[test]
fn nullable_enums_accept_null_valid_and_reject_bogus() {
    assert!(serde_json::from_value::<Waf>(json!({"vendor": "X", "confidence": null})).is_ok());
    assert!(serde_json::from_value::<Waf>(json!({"vendor": "X", "confidence": "high"})).is_ok());
    assert!(serde_json::from_value::<Waf>(json!({"vendor": "X", "confidence": "bogus"})).is_err());

    // Every new item accepts null optional enums.
    assert!(serde_json::from_value::<Cdn>(json!({"provider": "X", "caching": null})).is_ok());
    assert!(
        serde_json::from_value::<Challenge>(json!({"kind": "captcha", "severity_hint": null}))
            .is_ok()
    );
    assert!(serde_json::from_value::<RateLimit>(json!({"scope": "ip", "limit": null})).is_ok());
    assert!(serde_json::from_value::<ApiEndpoint>(
        json!({"protocol": "rest", "path": "/a", "source": null})
    )
    .is_ok());
}

#[test]
fn enum_serialization_names_match_schemas() {
    let cases = [
        (serde_json::to_value(Tool::Kensei).unwrap(), "kensei"),
        (
            serde_json::to_value(AnalysisStatus::Pending).unwrap(),
            "PENDING",
        ),
        (
            serde_json::to_value(AnalysisStatus::Cancelled).unwrap(),
            "CANCELLED",
        ),
        (
            serde_json::to_value(EventType::AnalysisStarted).unwrap(),
            "analysis_started",
        ),
        (serde_json::to_value(EventType::Log).unwrap(), "log"),
        (
            serde_json::to_value(Severity::Critical).unwrap(),
            "critical",
        ),
        (serde_json::to_value(Confidence::Low).unwrap(), "low"),
        (serde_json::to_value(Caching::Unknown).unwrap(), "unknown"),
        (
            serde_json::to_value(ChallengeKind::JsChallenge).unwrap(),
            "js_challenge",
        ),
        (
            serde_json::to_value(RateLimitScope::Session).unwrap(),
            "session",
        ),
        (serde_json::to_value(Protocol::Graphql).unwrap(), "graphql"),
        (
            serde_json::to_value(DiscoverySource::GrpcReflection).unwrap(),
            "grpc_reflection",
        ),
    ];
    for (value, expected) in cases {
        assert_eq!(value, expected);
    }
}

#[test]
fn event_roundtrip_keeps_type_field() {
    let event = Event {
        seq: 1,
        event_type: EventType::ItemFound,
        tool: Tool::Kabuki,
        analysis_id: "a1".into(),
        ts: "2026-08-08T10:00:01Z".into(),
        payload: Some(json!({"vendor": "Cloudflare"})),
    };
    let value = serde_json::to_value(&event).unwrap();
    assert_eq!(value["type"], "item_found");
    assert!(value.get("event_type").is_none());
    let restored: Event = serde_json::from_value(value).unwrap();
    assert_eq!(event, restored);
}

#[test]
fn new_items_roundtrip() {
    let waf = Waf {
        vendor: "Cloudflare".into(),
        product: None,
        confidence: Some(Confidence::High),
        detection_method: Some(DetectionMethod::Header),
        evidence: Some("cf-ray".into()),
        blocked: true,
        severity: Some(Severity::Info),
    };
    let cdn = Cdn {
        provider: "Fastly".into(),
        edge_nodes: Some(vec!["FRA".into()]),
        origin_hidden: true,
        caching: Some(Caching::Hit),
        evidence: None,
    };
    let challenge = Challenge {
        kind: ChallengeKind::Captcha,
        status_code: Some(403),
        headers: Some(json!({"cf-mitigated": "challenge"})),
        bypass_indicators: Some(vec!["no-op".into()]),
        response_time_ms: Some(1234.5),
        severity_hint: Some(Severity::Low),
    };
    let rate_limit = RateLimit {
        scope: RateLimitScope::Ip,
        limit: Some(120),
        window_seconds: Some(60),
        headers: None,
        threshold_estimate: Some(110),
        recommended_delay_ms: Some(500),
    };
    let api_endpoint = ApiEndpoint {
        protocol: Protocol::Rest,
        path: "/v1/users".into(),
        method: Some("GET".into()),
        host: Some("api.example.com".into()),
        params: Some(vec![xwa_sdk::ApiParam {
            name: "page".into(),
            location: Some("query".into()),
            param_type: Some("integer".into()),
            required: Some(false),
        }]),
        auth_required: Some(true),
        source: Some(DiscoverySource::Openapi),
        content_types: Some(vec!["application/json".into()]),
        version: Some("v1".into()),
    };
    let link = DiscoveredLink {
        url: "https://example.com".into(),
        status_code: Some(200),
        content_type: None,
    };
    let technology = Technology {
        category: "cdn".into(),
        name: "Cloudflare".into(),
        version: None,
        confidence: Some(Confidence::Medium),
        evidence: None,
    };
    let dependency = JsDependency {
        name: "rxjs".into(),
        version: Some("7.8.0".into()),
        source: None,
        package_manager: Some("npm".into()),
    };

    macro_rules! roundtrip {
        ($value:expr) => {{
            let json = serde_json::to_string(&$value).unwrap();
            let restored = serde_json::from_str(&json).unwrap();
            assert_eq!($value, restored);
        }};
    }

    roundtrip!(waf);
    roundtrip!(cdn);
    roundtrip!(challenge);
    roundtrip!(rate_limit);
    roundtrip!(api_endpoint);
    roundtrip!(link);
    roundtrip!(technology);
    roundtrip!(dependency);

    // None-valued optional fields disappear from the wire format.
    let json = serde_json::to_value(&cdn).unwrap();
    assert!(json.get("evidence").is_none());
    let json = serde_json::to_value(&challenge).unwrap();
    assert!(json.get("bypass_indicators").is_some());
}

#[test]
fn api_param_type_is_renamed() {
    let param = xwa_sdk::ApiParam {
        name: "q".into(),
        location: None,
        param_type: Some("string".into()),
        required: None,
    };
    let value = serde_json::to_value(&param).unwrap();
    assert_eq!(value["type"], "string");
    assert!(value.get("param_type").is_none());
    assert!(value.get("location").is_none());
    assert!(value.get("required").is_none());
}

#[test]
fn map_severity_matches_python_binding() {
    assert_eq!(map_severity("tengu", "Pass").unwrap(), Severity::Pass);
    assert_eq!(map_severity("tengu", "Info").unwrap(), Severity::Info);
    assert_eq!(map_severity("tengu", "Warning").unwrap(), Severity::Medium);
    assert_eq!(map_severity("tengu", "Error").unwrap(), Severity::High);
    assert_eq!(
        map_severity("samurai", "critical").unwrap(),
        Severity::Critical
    );
    assert_eq!(map_severity("kensei", "low").unwrap(), Severity::Low);

    let err = map_severity("samurai", "Warning").unwrap_err();
    assert!(err.to_string().contains("Warning"));
    assert!(map_severity("tengu", "bogus").is_err());
}

#[test]
fn raw_json_analysis_deserializes() {
    let raw = json!({
        "id": "a1",
        "tool": "kabuki",
        "target": "https://example.com",
        "status": "COMPLETED",
        "created_at": "2026-08-08T10:00:00Z",
        "error": {"code": "X", "message": "y"},
        "summary": {"total_items": 1, "by_severity": {"info": 1}}
    });
    let analysis: Analysis = serde_json::from_value(raw).unwrap();
    assert_eq!(analysis.tool, Tool::Kabuki);
    assert_eq!(analysis.status, AnalysisStatus::Completed);
    assert_eq!(analysis.summary.unwrap().total_items, Some(1));
    assert!(analysis.error.is_some());
}
