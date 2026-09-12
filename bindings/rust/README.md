# xwa-sdk — Rust bindings

Shared data models for the XWA ecosystem, mirroring the canonical JSON Schemas
in `xwa-sdk/schemas` (draft 2020-12). Intended for the Axum backends
(`shinobi`, `tengu`).

```toml
[dependencies]
xwa-sdk = { path = "../xwa-sdk/bindings/rust" }
```

```rust
use xwa_sdk::{map_severity, Analysis, AnalysisStatus, Tool};

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

- `serde` + `serde_json` are the only required dependencies.
- `thiserror` is optional: `cargo build --features thiserror` derives
  `Display`/`Error` for `SdkError`; the default build ships manual impls.
- `map_severity("tengu", "Warning") -> Ok(Severity::Medium)` mirrors the
  Python and TypeScript bindings.

## Tests

```bash
cargo fmt --check && cargo test && cargo test --features thiserror
```
