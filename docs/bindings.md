# Language Bindings

Both bindings mirror the canonical schemas and stay in lockstep with them. Add a binding only if a module stack requires it; the schemas themselves are always the source of truth.

## Python (`bindings/python`, package `xwa_sdk`)

Targets the FastAPI backends (samurai, kensei).

### Install

```bash
pip install -e bindings/python
```

Requires Python 3.10+. Runtime dependency: `jsonschema`.

### Models

```python
from xwa_sdk import Analysis, Finding, Event, Error, to_dict, from_dict

analysis = Analysis(
    id="scan-42",
    tool="samurai",
    target="https://example.com",
    status="RUNNING",
    created_at="2026-08-08T10:00:00Z",
)
```

All models are dataclasses. `to_dict` serializes to a plain dict, omitting `None` values. `from_dict` rebuilds a model, converting nested `Summary` and `Error` fields.

### Severity mapping

```python
from xwa_sdk import map_severity

map_severity("tengu", "Warning")   # -> "medium"
map_severity("tengu", "Error")     # -> "high"
map_severity("samurai", "critical")  # -> "critical"
```

Raises `ValueError` for unknown severity values.

### Validation

```python
from xwa_sdk import validate_analysis, validate_finding, validate_event
from xwa_sdk.validation import ValidationError

try:
    validate_finding({"tool": "tengu", "severity": "medium", "title": "t", "description": "d"})
except ValidationError as exc:
    print(exc.message)
```

Convenience predicates return booleans without raising:

```python
from xwa_sdk import is_valid_finding, is_valid_event, is_valid_analysis
```

`validate_item(kind, data)` validates module items by schema name: `"link"`, `"technology"`, `"route"`, `"dependency"`.

### Tests

```bash
python -m pytest bindings/python/tests
```

## TypeScript (`bindings/typescript`, package `xwa-sdk-types`)

Targets the Angular frontends.

### Install

```bash
npm install   # in bindings/typescript
npm run build # compiles to dist/ (types + declarations)
```

### Types

```ts
import {
  Analysis, Finding, Event, ErrorInfo,
  Technology, DiscoveredLink, DiscoveredRoute, JsDependency,
  Tool, Severity, AnalysisStatus, EventType,
} from "xwa-sdk-types";
```

### Severity mapping and type guards

```ts
import { mapSeverity, isFinding, isAnalysis, isEvent } from "xwa-sdk-types";

const severity = mapSeverity("tengu", "Warning"); // "medium"

if (isFinding(payload)) {
  payload.severity; // typed as Severity
}
```

`mapSeverity` throws `Error` for unknown severity values. Type guards narrow unknown payloads to the typed interfaces.
