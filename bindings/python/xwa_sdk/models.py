"""XWA SDK — shared models for the XWA ecosystem.

Mirrors the canonical JSON Schemas in xwa-sdk/schemas.
Zero-dependency core (stdlib only); validation lives in xwa_sdk.validation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

TOOLS = ("samurai", "shinobi", "tengu", "kensei", "kabuki", "yari", "musha", "azuma")
ANALYSIS_STATUS = ("PENDING", "RUNNING", "COMPLETED", "ERROR", "CANCELLED")
SEVERITIES = ("pass", "info", "low", "medium", "high", "critical")
EVENT_TYPES = (
    "analysis_started",
    "analysis_progress",
    "item_found",
    "analysis_completed",
    "analysis_error",
    "log",
)


@dataclass
class Error:
    code: str
    message: str
    detail: dict | None = None
    retryable: bool = False


@dataclass
class Summary:
    total_items: int | None = None
    by_severity: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)


@dataclass
class Analysis:
    id: str
    tool: str
    target: str
    status: str
    created_at: str
    tool_version: str | None = None
    analysis_type: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    error: Error | None = None
    summary: Summary | None = None


@dataclass
class Finding:
    tool: str
    severity: str
    title: str
    description: str
    id: str | None = None
    category: str | None = None
    check: str | None = None
    target_url: str | None = None
    evidence: dict | None = None
    cvss_score: str | None = None
    confidence: str | None = None
    detected_at: str | None = None


@dataclass
class Event:
    seq: int
    type: str
    tool: str
    analysis_id: str
    ts: str
    payload: Any = None


# ── Module items ────────────────────────────────────────────────────────────

@dataclass
class DiscoveredLink:
    url: str
    status_code: int | None = None
    content_type: str | None = None


@dataclass
class Technology:
    category: str
    name: str
    version: str | None = None
    confidence: str | None = None
    evidence: str | None = None


@dataclass
class DiscoveredRoute:
    path: str
    framework: str | None = None
    route_type: str | None = None
    module: str | None = None


@dataclass
class JsDependency:
    name: str
    version: str | None = None
    source: str | None = None
    package_manager: str | None = None


# ── (de)serialization ───────────────────────────────────────────────────────

def to_dict(obj: Any) -> dict:
    """Convert a dataclass instance (nested included) to a plain dict, omitting None values."""
    data = asdict(obj)
    return {k: v for k, v in data.items() if v is not None}


def _unwrap_optional(ftype: Any) -> Any:
    """Return the non-None type of an Optional/Union annotation, if any."""
    origin = get_origin(ftype)
    if origin is Union or origin is UnionType:
        args = [a for a in get_args(ftype) if a is not type(None)]
        return args[0] if len(args) == 1 else None
    return ftype


def from_dict(cls: type, data: dict) -> Any:
    """Build a dataclass instance from a dict, recursively converting known fields."""
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")
    fields = get_type_hints(cls)
    kwargs: dict[str, Any] = {}
    for name, ftype in fields.items():
        if name not in data:
            continue
        value = data[name]
        inner = _unwrap_optional(ftype)
        if is_dataclass(inner) and isinstance(value, dict):
            kwargs[name] = from_dict(inner, value)
        elif inner == Summary and isinstance(value, dict):
            kwargs[name] = Summary(**value)
        elif inner == Error and isinstance(value, dict):
            kwargs[name] = Error(**value)
        else:
            kwargs[name] = value
    return cls(**kwargs)


# ── Severity mapping helpers ────────────────────────────────────────────────

MODULE_SEVERITY_MAP = {
    # tengu internal severities → unified
    "tengu": {"Pass": "pass", "Info": "info", "Warning": "medium", "Error": "high"},
}


def map_severity(tool: str, severity: str) -> str:
    """Map a module-internal severity to the unified scale."""
    mapping = MODULE_SEVERITY_MAP.get(tool)
    if mapping and severity in mapping:
        return mapping[severity]
    if severity in SEVERITIES:
        return severity
    raise ValueError(f"Unknown severity '{severity}' for tool '{tool}'")
