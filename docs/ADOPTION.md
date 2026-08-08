# Adopting xwa-sdk

How XWA modules emit and consume shared data. The canonical definitions live in `schemas/` (JSON Schema); language bindings mirror them. See [README.md](README.md) for the documentation index, [schemas.md](schemas.md) for the field-by-field reference and [bindings.md](bindings.md) for installation and usage.

## Core concepts

- **Analysis** — the unit of work (scan, audit, profile). Created when work starts, updated until a terminal status (`COMPLETED` | `ERROR` | `CANCELLED`).
- **Finding** — a single observation, normalized to the unified severity scale.
- **Event** — streaming envelope for live results (WebSocket / queues).
- **Error** — structured failure, attached to an analysis or event.

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

## Emitting an event (TypeScript)

```ts
import { Event, isFinding } from "xwa-sdk-types";

const event: Event = {
  seq: 1,
  type: "item_found",
  tool: "tengu",
  analysis_id: "audit-7",
  ts: new Date().toISOString(),
  payload: { /* finding */ },
};
if (isFinding(event.payload)) {
  // ...
}
```

## Validation

- Python: `xwa_sdk.validation.validate_finding(data)` raises `jsonschema.exceptions.ValidationError` on invalid payloads.
- Schemas are bundled inside the Python package under `xwa_sdk/schemas/` and copied 1:1 from `schemas/` — update both when changing a schema (see [versioning.md](versioning.md)).
