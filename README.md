<h1 align="center">XWA SDK</h1>

<div align="center">
<p><em>Shared data schemas and API contracts — part of the <a href="https://github.com/xwebanalysis">XWA ecosystem</a></em></p>
</div>

<hr>

<p><strong>Status: <em>Active</em></strong> (v0.1.0)</p>

<p>Shared contracts consumed by all XWA tools for cross-module integration. JSON Schema is the source of truth; bindings mirror it per language.</p>

## Layout

| Path | Contents |
|------|----------|
| `schemas/` | Canonical JSON Schemas: `analysis`, `finding`, `event`, `error` + module items |
| `bindings/python/` | `xwa_sdk` package — dataclasses + schema validation + severity mapping |
| `bindings/typescript/` | `xwa-sdk-types` — types, type guards, severity mapping |
| `docs/` | Adoption guide, severity mapping, versioning policy |

## Quick start (Python)

```bash
pip install -e bindings/python
```

```python
from xwa_sdk import Analysis, to_dict, validate_analysis

analysis = Analysis(
    id="scan-42", tool="samurai", target="https://example.com",
    status="RUNNING", created_at="2026-08-08T10:00:00Z",
)
validate_analysis(to_dict(analysis))
```

## Quick start (TypeScript)

```bash
npm install --save-dev typescript && npx tsc   # in bindings/typescript
```

```ts
import { Event, isFinding } from "./bindings/typescript/src";
```

## Docs

- [docs/README.md](docs/README.md) — documentation index
- [ADOPTION.md](docs/ADOPTION.md) — how modules emit and consume shared data
- [schemas.md](docs/schemas.md) — field-by-field schema reference
- [bindings.md](docs/bindings.md) — language binding usage
- [versioning.md](docs/versioning.md) — versioning and compatibility policy
- [ROADMAP.md](ROADMAP.md) — development phases
