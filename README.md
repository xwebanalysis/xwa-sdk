<h1 align="center">XWA SDK</h1>

<div align="center">
<p><em>Shared data schemas and API contracts — part of the <a href="https://github.com/xwebanalysis">XWA ecosystem</a></em></p>
</div>

<hr>

<p><strong>Status: <em>Active</em></strong> (v0.2.1)</p>

<p>Shared contracts consumed by all XWA tools for cross-module integration. JSON Schema is the source of truth; bindings mirror it per language.</p>

## Layout

| Path | Contents |
|------|----------|
| `schemas/` | Canonical JSON Schemas: `analysis`, `finding`, `event`, `error` + module items |
| `bindings/python/` | `xwa_sdk` package — dataclasses + offline schema validation + severity mapping |
| `bindings/typescript/` | `xwa-sdk-types` — types, type guards, severity mapping, `node:test` suite |
| `bindings/rust/` | `xwa-sdk` crate — serde models + `map_severity`, `cargo test` suite |
| `scripts/` | `sync_schemas.py` keeps the bundled Python copy identical to `schemas/` |
| `docs/` | Adoption guide, schema reference, bindings, versioning policy |
| `CHANGELOG.md` | Release history (Keep a Changelog, simplified) |

## Quick start (Python)

```bash
pip install -e bindings/python
```

```python
from xwa_sdk import Analysis, Waf, to_dict, validate_analysis, validate_item

analysis = Analysis(
    id="scan-42", tool="kabuki", target="https://example.com",
    status="RUNNING", created_at="2026-08-08T10:00:00Z",
)
validate_analysis(to_dict(analysis))                    # offline, no network
validate_item("waf", to_dict(Waf(vendor="Cloudflare", confidence=None)))
```

## Quick start (TypeScript)

```bash
cd bindings/typescript
npm install
npm run build
```

```ts
import { Event, isFinding, mapSeverity, isWaf } from "xwa-sdk-types";

const severity = mapSeverity("tengu", "Warning"); // "medium"
if (isWaf(payload)) {
  payload.vendor;
}
```

## Quick start (Rust)

```toml
[dependencies]
xwa-sdk = { path = "../xwa-sdk/bindings/rust" }
```

```rust
use xwa_sdk::{map_severity, Severity};
assert_eq!(map_severity("tengu", "Error").unwrap(), Severity::High);
```

## Tests

```bash
# Python (from the repo root; verified on Python 3.14)
python3 -m venv bindings/python/.venv
bindings/python/.venv/bin/pip install -e "bindings/python[test]"
cd bindings/python && .venv/bin/pytest -q

# TypeScript
cd bindings/typescript && npm test

# Rust
cd bindings/rust && cargo test
```

## License

The bindings declare `MIT` in their package metadata (a build-tooling
requirement), but the ecosystem owner has **not** published an ecosystem-wide
`LICENSE` file yet. The license is therefore not final; see the note at the top
of [CHANGELOG.md](CHANGELOG.md).

## Docs

- [docs/README.md](docs/README.md) — documentation index
- [docs/ADOPTION.md](docs/ADOPTION.md) — how modules emit and consume shared data
- [docs/schemas.md](docs/schemas.md) — field-by-field schema reference
- [docs/bindings.md](docs/bindings.md) — language binding usage
- [docs/versioning.md](docs/versioning.md) — versioning, compatibility and schema sync
- [CHANGELOG.md](CHANGELOG.md) — release history
- [ROADMAP.md](ROADMAP.md) — development phases
