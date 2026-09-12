//! XWA SDK — shared data models for the XWA ecosystem.
//!
//! Mirrors the canonical JSON Schemas in `xwa-sdk/schemas` (draft 2020-12):
//! `Analysis`, `Finding`, `Event`, `Error`, `Summary` and the module items.
//! Every model is `serde` (de)serializable and optional fields are skipped
//! when `None`, matching the Python binding's `to_dict`.
//!
//! ```rust
//! use xwa_sdk::{Analysis, AnalysisStatus, Error, Tool};
//!
//! let analysis = Analysis {
//!     id: "scan-42".into(),
//!     tool: Tool::Samurai,
//!     target: "https://example.com".into(),
//!     status: AnalysisStatus::Error,
//!     created_at: "2026-08-08T10:00:00Z".into(),
//!     error: Some(Error {
//!         code: "TIMEOUT".into(),
//!         message: "no response".into(),
//!         ..Default::default()
//!     }),
//!     ..Default::default()
//! };
//! let json = serde_json::to_string(&analysis).unwrap();
//! assert!(!json.contains("summary"));
//! ```

use std::collections::BTreeMap;
use std::fmt;
use std::str::FromStr;

use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Producing module.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Tool {
    Samurai,
    Shinobi,
    Tengu,
    Kensei,
    Kabuki,
    Yari,
    Musha,
    Azuma,
}

/// Analysis lifecycle state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum AnalysisStatus {
    #[serde(rename = "PENDING")]
    Pending,
    #[serde(rename = "RUNNING")]
    Running,
    #[serde(rename = "COMPLETED")]
    Completed,
    #[serde(rename = "ERROR")]
    Error,
    #[serde(rename = "CANCELLED")]
    Cancelled,
}

/// Unified severity scale.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Severity {
    Pass,
    Info,
    Low,
    Medium,
    High,
    Critical,
}

impl FromStr for Severity {
    type Err = SdkError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "pass" => Ok(Self::Pass),
            "info" => Ok(Self::Info),
            "low" => Ok(Self::Low),
            "medium" => Ok(Self::Medium),
            "high" => Ok(Self::High),
            "critical" => Ok(Self::Critical),
            other => Err(SdkError::UnknownSeverity {
                tool: String::new(),
                severity: other.to_string(),
            }),
        }
    }
}

/// Streaming event type.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    AnalysisStarted,
    AnalysisProgress,
    ItemFound,
    AnalysisCompleted,
    AnalysisError,
    Log,
}

/// Detection confidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Confidence {
    High,
    Medium,
    Low,
}

/// WAF detection signal.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum DetectionMethod {
    Header,
    Cookie,
    Body,
    Status,
    Dns,
    Tls,
}

/// CDN cache status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Caching {
    Hit,
    Miss,
    Stale,
    Unknown,
}

/// Bot challenge family.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ChallengeKind {
    Captcha,
    JsChallenge,
    BlockPage,
    Interstitial,
}

/// Rate limit scope.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RateLimitScope {
    Ip,
    Session,
    Global,
    Unknown,
}

/// API protocol family.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Protocol {
    Rest,
    Graphql,
    Grpc,
}

/// How an API endpoint was discovered.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DiscoverySource {
    Openapi,
    GraphqlIntrospection,
    GrpcReflection,
    JsCrawl,
    Html,
}

/// Error raised by SDK helpers (e.g. [`map_severity`]).
#[derive(Debug, Clone, PartialEq, Eq)]
#[cfg_attr(feature = "thiserror", derive(thiserror::Error))]
pub enum SdkError {
    /// The severity value is not part of the unified scale and has no mapping.
    #[cfg_attr(
        feature = "thiserror",
        error("unknown severity '{severity}' for tool '{tool}'")
    )]
    UnknownSeverity { tool: String, severity: String },
}

#[cfg(not(feature = "thiserror"))]
impl fmt::Display for SdkError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SdkError::UnknownSeverity { tool, severity } => {
                write!(f, "unknown severity '{severity}' for tool '{tool}'")
            }
        }
    }
}

#[cfg(not(feature = "thiserror"))]
impl std::error::Error for SdkError {}

/// Structured failure attached to an analysis.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Error {
    pub code: String,
    pub message: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub detail: Option<Value>,
    #[serde(default)]
    pub retryable: bool,
}

/// Aggregated result counts.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Summary {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub total_items: Option<i64>,
    #[serde(default)]
    pub by_severity: BTreeMap<String, i64>,
    #[serde(default)]
    pub by_category: BTreeMap<String, i64>,
}

/// Top-level unit of work produced by a tool.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Analysis {
    pub id: String,
    pub tool: Tool,
    pub target: String,
    pub status: AnalysisStatus,
    pub created_at: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tool_version: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub analysis_type: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub finished_at: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub error: Option<Error>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub summary: Option<Summary>,
}

impl Default for Analysis {
    fn default() -> Self {
        Self {
            id: String::new(),
            tool: Tool::Samurai,
            target: String::new(),
            status: AnalysisStatus::Pending,
            created_at: String::new(),
            tool_version: None,
            analysis_type: None,
            started_at: None,
            finished_at: None,
            error: None,
            summary: None,
        }
    }
}

/// A single observation mapped to the unified severity scale.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Finding {
    pub tool: Tool,
    pub severity: Severity,
    pub title: String,
    pub description: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub category: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub check: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub target_url: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub evidence: Option<Value>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cvss_score: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub detected_at: Option<String>,
}

/// Streaming envelope for live analysis progress.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Event {
    pub seq: i64,
    #[serde(rename = "type")]
    pub event_type: EventType,
    pub tool: Tool,
    pub analysis_id: String,
    pub ts: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub payload: Option<Value>,
}

// ── Module items ────────────────────────────────────────────────────────────

/// samurai: link discovered during crawling.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiscoveredLink {
    pub url: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub status_code: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub content_type: Option<String>,
}

/// kensei: detected technology stack component.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Technology {
    pub category: String,
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub evidence: Option<String>,
}

/// kensei: SPA route discovered during profiling.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiscoveredRoute {
    pub path: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub framework: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub route_type: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub module: Option<String>,
}

/// kensei: JavaScript dependency detected from bundles or source maps.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct JsDependency {
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub package_manager: Option<String>,
}

/// kabuki: Web Application Firewall fingerprint.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Waf {
    pub vendor: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub product: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub confidence: Option<Confidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub detection_method: Option<DetectionMethod>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub evidence: Option<String>,
    #[serde(default)]
    pub blocked: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub severity: Option<Severity>,
}

/// kabuki: Content Delivery Network fingerprint.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Cdn {
    pub provider: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub edge_nodes: Option<Vec<String>>,
    #[serde(default)]
    pub origin_hidden: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub caching: Option<Caching>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub evidence: Option<String>,
}

/// kabuki: bot challenge or interstitial page.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Challenge {
    pub kind: ChallengeKind,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub status_code: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub headers: Option<Value>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bypass_indicators: Option<Vec<String>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub response_time_ms: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub severity_hint: Option<Severity>,
}

/// kabuki: rate limiting profile estimate.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RateLimit {
    pub scope: RateLimitScope,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub limit: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub window_seconds: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub headers: Option<Value>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub threshold_estimate: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub recommended_delay_ms: Option<i64>,
}

/// yari: a discovered API parameter.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ApiParam {
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub location: Option<String>,
    #[serde(rename = "type", default, skip_serializing_if = "Option::is_none")]
    pub param_type: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub required: Option<bool>,
}

/// yari: API endpoint discovered through specs, reflection or crawling.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ApiEndpoint {
    pub protocol: Protocol,
    pub path: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub method: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub host: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub params: Option<Vec<ApiParam>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub auth_required: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source: Option<DiscoverySource>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub content_types: Option<Vec<String>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

// ── Severity mapping ────────────────────────────────────────────────────────

/// Map a module-internal severity to the unified scale (mirrors Python).
///
/// ```
/// use xwa_sdk::{map_severity, Severity};
///
/// assert_eq!(map_severity("tengu", "Warning").unwrap(), Severity::Medium);
/// assert_eq!(map_severity("tengu", "Error").unwrap(), Severity::High);
/// assert_eq!(map_severity("samurai", "critical").unwrap(), Severity::Critical);
/// assert!(map_severity("samurai", "Warning").is_err());
/// ```
pub fn map_severity(tool: &str, severity: &str) -> Result<Severity, SdkError> {
    if tool == "tengu" {
        match severity {
            "Pass" => return Ok(Severity::Pass),
            "Info" => return Ok(Severity::Info),
            "Warning" => return Ok(Severity::Medium),
            "Error" => return Ok(Severity::High),
            _ => {}
        }
    }
    severity.parse().map_err(|_| SdkError::UnknownSeverity {
        tool: tool.to_string(),
        severity: severity.to_string(),
    })
}
