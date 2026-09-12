# xwa-sdk — Python bindings

Dataclasses, offline JSON Schema validation and severity mapping for the XWA
ecosystem. The canonical schemas live in the repository root `schemas/` and are
bundled 1:1 inside this package.

## Install

```bash
pip install -e ".[test]"
```

Requires Python 3.10+ and `jsonschema>=4`. Ships a `py.typed` marker.

## Usage

```python
from xwa_sdk import Analysis, Waf, to_dict, validate_analysis, validate_item, map_severity

analysis = Analysis(
    id="scan-42", tool="samurai", target="https://example.com",
    status="RUNNING", created_at="2026-08-08T10:00:00Z",
)
validate_analysis(to_dict(analysis))  # offline; nested $refs resolved locally

waf = Waf(vendor="Cloudflare", confidence=None, detection_method="header")
validate_item("waf", to_dict(waf))

map_severity("tengu", "Warning")  # "medium"
```

- `to_dict` omits `None` recursively (nested dataclasses, dicts and lists).
- `validate_*` raises `jsonschema.exceptions.ValidationError`; `is_valid_*`
  returns a bool and never leaks referencing errors.
- Item models: `DiscoveredLink`, `Technology`, `DiscoveredRoute`,
  `JsDependency`, `Waf`, `Cdn`, `Challenge`, `RateLimit`, `ApiEndpoint`.
  Kinds for `validate_item`: see `xwa_sdk.ITEM_KINDS`.

## Tests

```bash
~/.local/bin/uv venv --python 3.13 --seed .venv
.venv/bin/pip install "jsonschema>=4.0" "pytest>=8"
.venv/bin/pytest -q
```

The suite includes a test that fails if `xwa_sdk/schemas/` drifts from the
canonical `schemas/` tree (fix it with `python scripts/sync_schemas.py`).

## License note

`pyproject.toml` declares `license = "MIT"` because build tooling requires a
value, but the ecosystem owner has not published a `LICENSE` file. The license
is not final — see the note at the top of the repository `CHANGELOG.md`.
