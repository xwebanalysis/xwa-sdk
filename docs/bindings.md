# Language Bindings

All bindings mirror the canonical schemas and stay in lockstep with them. Add a binding only if a module stack requires it; the schemas themselves are always the source of truth.

| Binding | Path | Consumers | Dependency |
|---------|------|-----------|------------|
| Python | `bindings/python` (`xwa_sdk`) | FastAPI backends (samurai, kensei, musha, azuma, kabuki, yari) | `jsonschema` |
| TypeScript | `bindings/typescript` (`xwa-sdk-types`) | Angular frontends | none (types only) |
| Rust | `bindings/rust` (`xwa-sdk`) | Axum backends (shinobi, tengu) | `serde`, `serde_json` (`thiserror` optional) |

## Python (`bindings/python`, package `xwa_sdk`)

### Install

```bash
pip install -e bindings/python
# or with test dependencies:
pip install -e "bindings/python[test]"
```

Requires Python 3.10+. Runtime dependency: `jsonschema`. The package ships a
`py.typed` marker and bundles the schemas inside the wheel.

### Models

```python
from xwa_sdk import Analysis, Finding, Event, Error, Waf, to_dict, from_dict

analysis = Analysis(
    id="scan-42",
    tool="samurai",
    target="https://example.com",
    status="RUNNING",
    created_at="2026-08-08T10:00:00Z",
)
```

All models are dataclasses. `to_dict` serializes to a plain dict, omitting
`None` values **recursively** (nested dataclasses, dicts and lists).
`from_dict` rebuilds a model, converting nested dataclass fields. Available
item models: `DiscoveredLink`, `Technology`, `DiscoveredRoute`, `JsDependency`,
`Waf`, `Cdn`, `Challenge`, `RateLimit`, `ApiEndpoint`.

### Severity mapping

```python
from xwa_sdk import map_severity

map_severity("tengu", "Warning")     # -> "medium"
map_severity("tengu", "Error")       # -> "high"
map_severity("samurai", "critical")  # -> "critical"
```

Raises `ValueError` for unknown severity values. Tool-specific names are only
translated for their own tool.

### Validation (offline)

```python
from xwa_sdk import validate_analysis, validate_finding, validate_item
from xwa_sdk.validation import ValidationError

try:
    validate_finding({"tool": "tengu", "severity": "medium", "title": "t", "description": "d"})
except ValidationError as exc:
    print(exc.message)
```

`validate_*` always raises `jsonschema.exceptions.ValidationError` on invalid
payloads. Nested `$ref`s (for example `analysis.error`) resolve from the
schemas bundled in the package through a local `referencing.Registry`: **no
network access**.

Convenience predicates return booleans without raising:

```python
from xwa_sdk import is_valid_analysis, is_valid_finding, is_valid_event, is_valid_item
```

`validate_item(kind, data)` validates module items by schema name:
`"link"`, `"technology"`, `"route"`, `"dependency"`, `"waf"`, `"cdn"`,
`"challenge"`, `"rate_limit"`, `"api_endpoint"` (see `xwa_sdk.ITEM_KINDS`).

### Tests

```bash
cd bindings/python
~/.local/bin/uv venv --python 3.13 --seed .venv
.venv/bin/pip install "jsonschema>=4.0" "pytest>=8"
.venv/bin/pytest -q
```

## TypeScript (`bindings/typescript`, package `xwa-sdk-types`)

### Install

```bash
npm install   # in bindings/typescript
npm run build # compiles to dist/ (types + declarations)
```

`prepare`/`prepublishOnly` run the build automatically; the package publishes
`dist/` plus the README with `exports`/`types` wired.

### Types

```ts
import {
  Analysis, Finding, Event, ErrorInfo,
  Technology, DiscoveredLink, DiscoveredRoute, JsDependency,
  Waf, Cdn, Challenge, RateLimit, ApiEndpoint, ApiParam,
  Tool, Severity, AnalysisStatus, EventType,
} from "xwa-sdk-types";
```

### Severity mapping and type guards

```ts
import { mapSeverity, isFinding, isAnalysis, isEvent, isWaf } from "xwa-sdk-types";

const severity = mapSeverity("tengu", "Warning"); // "medium"

if (isFinding(payload)) {
  payload.severity; // typed as Severity
}
if (isWaf(payload)) {
  payload.vendor;
}
```

`mapSeverity` throws `Error` for unknown severity values and only translates
`tengu`-specific names (same behavior as Python). Type guards narrow unknown
payloads to the typed interfaces; guards for the new items: `isWaf`, `isCdn`,
`isChallenge`, `isRateLimit`, `isApiEndpoint`.

### Tests

```bash
cd bindings/typescript
npm test   # builds, then runs node:test
```

## Rust (`bindings/rust`, crate `xwa-sdk`)

### Install

```toml
[dependencies]
xwa-sdk = { path = "../xwa-sdk/bindings/rust" }
serde_json = "1"
```

Edition 2021, MSRV 1.75. `serde` + `serde_json` are required; `thiserror` is
optional (`features = ["thiserror"]`) and only affects `SdkError` impls.

### Models

```rust
use xwa_sdk::{Analysis, AnalysisStatus, Error, Tool};

let analysis = Analysis {
    id: "scan-42".into(),
    tool: Tool::Samurai,
    target: "https://example.com".into(),
    status: AnalysisStatus::Running,
    created_at: "2026-08-08T10:00:00Z".into(),
    ..Default::default()
};
let json = serde_json::to_string(&analysis).unwrap(); // None fields are skipped
```

All models derive `Serialize`/`Deserialize`; optional fields use
`skip_serializing_if = "Option::is_none"`. Enums (`Tool`, `AnalysisStatus`,
`EventType`, `Severity`, `Confidence`, `DetectionMethod`, `Caching`,
`ChallengeKind`, `RateLimitScope`, `Protocol`, `DiscoverySource`) reject
unknown values at deserialization time, mirroring the JSON Schemas.

### Severity mapping

```rust
use xwa_sdk::{map_severity, Severity};

assert_eq!(map_severity("tengu", "Warning").unwrap(), Severity::Medium);
assert_eq!(map_severity("samurai", "critical").unwrap(), Severity::Critical);
```

### Tests

```bash
cd bindings/rust
cargo fmt --check
cargo test
cargo test --features thiserror
```

## Keeping the copies in sync

Edit only `schemas/` and run:

```bash
python scripts/sync_schemas.py          # copy canonical -> bundled Python schemas
python scripts/sync_schemas.py --check  # CI/test mode; exits 1 on drift
```

Then update the language types and `docs/schemas.md`, and bump the version per
[versioning.md](versioning.md). The Python test suite fails if the bundled copy
drifts.
