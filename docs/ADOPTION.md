# Adopting xwa-sdk

How XWA modules emit and consume shared data. The canonical definitions live in `schemas/` (JSON Schema); language bindings mirror them. See [README.md](README.md) for the documentation index, [schemas.md](schemas.md) for the field-by-field reference and [bindings.md](bindings.md) for installation and usage.

## Core concepts

- **Analysis** — the unit of work (scan, audit, profile). Created when work starts, updated until a terminal status (`COMPLETED` | `ERROR` | `CANCELLED`).
- **Finding** — a single observation, normalized to the unified severity scale.
- **Event** — streaming envelope for live results (WebSocket / queues).
- **Error** — structured failure, attached to an analysis or event.
- **Module item** — module-specific result entity (`link`, `technology`, `route`, `dependency`, `waf`, `cdn`, `challenge`, `rate_limit`, `api_endpoint`).

## Severity mapping

| Module severity | Unified |
|-----------------|---------|
| samurai `info`/`low`/`medium`/`high`/`critical` | same |
| tengu `Pass` | `pass` |
| tengu `Info` | `info` |
| tengu `Warning` | `medium` |
| tengu `Error` | `high` |
| kensei confidence `low`/`medium`/`high` | `info`/`medium`/`high` |

## Emitting a finding (Python)

```python
from xwa_sdk import Analysis, Finding, Event, to_dict, map_severity

analysis = Analysis(
    id="scan-42", tool="samurai", target="https://example.com",
    status="RUNNING", created_at="2026-08-08T10:00:00Z",
)
finding = Finding(
    tool="samurai", severity=map_severity("samurai", "high"),
    title="SQL Injection", description="Blind SQLi in /search",
    category="sqli", evidence={"poc_payload": "' OR 1=1--"},
    cvss_score="9.8",
)
event = Event(seq=1, type="item_found", tool="samurai",
              analysis_id="scan-42", ts="2026-08-08T10:00:01Z",
              payload=to_dict(finding))
```

## Emitting a kabuki item (Python)

kabuki fingerprints WAFs, CDNs, bot challenges and rate limits. Optional enum
fields accept `null`, and `to_dict` drops `None` recursively, so the payload
validates as-is:

```python
from xwa_sdk import ApiEndpoint, Cdn, Challenge, Event, RateLimit, Waf, to_dict, validate_item

waf = Waf(
    vendor="Cloudflare", product=None, confidence="high",
    detection_method="header", evidence="cf-ray: 8f…", blocked=True, severity="info",
)
validate_item("waf", to_dict(waf))  # offline

cdn = Cdn(provider="Fastly", edge_nodes=["FRA", "AMS"], origin_hidden=True, caching=None)
challenge = Challenge(kind="js_challenge", status_code=503, headers={"server": "cloudflare"})
rate = RateLimit(scope="ip", limit=120, window_seconds=60, recommended_delay_ms=500)

analysis = Analysis(
    id="kabuki-7", tool="kabuki", target="https://example.com",
    status="RUNNING", created_at="2026-08-08T10:00:00Z",
    analysis_type="waf_profile",
)
event = Event(
    seq=1, type="item_found", tool="kabuki", analysis_id="kabuki-7",
    ts="2026-08-08T10:00:01Z", payload=to_dict(waf),
)
```

## Emitting a yari item (Python)

yari discovers REST/GraphQL/gRPC endpoints:

```python
from xwa_sdk import ApiEndpoint, to_dict, validate_item

endpoint = ApiEndpoint(
    protocol="rest", path="/v1/users", method="GET", host="api.example.com",
    params=[{"name": "page", "location": "query", "type": "integer", "required": False}],
    auth_required=True, source="openapi",
    content_types=["application/json"], version="v1",
)
validate_item("api_endpoint", to_dict(endpoint))
```

## Emitting an event (TypeScript)

```ts
import { Event, isFinding, isWaf, mapSeverity } from "xwa-sdk-types";

const event: Event = {
  seq: 1,
  type: "item_found",
  tool: "tengu",
  analysis_id: "audit-7",
  ts: new Date().toISOString(),
  payload: { /* finding or item */ },
};
if (isFinding(event.payload)) {
  event.payload.severity; // Severity
}
if (isWaf(event.payload)) {
  event.payload.vendor; // string
}
const severity = mapSeverity("tengu", "Warning"); // "medium"
```

## Consuming events (Rust)

```rust
use xwa_sdk::{map_severity, Event, Severity};

let event: Event = serde_json::from_str(raw)?;
if matches!(event.event_type, xwa_sdk::EventType::ItemFound) {
    // payload carries a finding or module item
}
assert_eq!(map_severity("tengu", "Warning")?, Severity::Medium);
```

## Validation

- Python: `xwa_sdk.validation.validate_finding(data)` raises `jsonschema.exceptions.ValidationError` on invalid payloads. `validate_*` never leaks referencing errors and resolves nested `$ref`s from a bundled local registry (fully offline).
- Schemas are bundled inside the Python package under `xwa_sdk/schemas/` and copied 1:1 from `schemas/` by `scripts/sync_schemas.py`; a test fails if both trees drift (see [versioning.md](versioning.md)).
- Rust validates enum values via typed `serde` enums at deserialization time; extra properties are ignored, matching `additionalProperties: true`.
- TypeScript narrows unknown payloads with type guards (`isAnalysis`, `isFinding`, `isEvent`, `isWaf`, `isCdn`, `isChallenge`, `isRateLimit`, `isApiEndpoint`).
