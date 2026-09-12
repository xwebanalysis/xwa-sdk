# XWA SDK Development Roadmap

This document tracks the strategic steps required to evolve the XWA SDK into the shared data and contract layer of the XWA ecosystem.
This file is formatted to be synced automatically with GitHub Issues using the `xgh` roadmap standard.

Status legend: `[x]` done in-tree, `[ ]` pending.

## Core Schemas <!-- phase:schemas -->

- [x] Define base result and finding schemas
- [x] Define scan and target descriptors
- [x] Define task and progress event schemas
- [x] Define error handling and status envelope
- [x] Define samurai/kensei item schemas (`link`, `technology`, `route`, `dependency`)
- [x] Define kabuki item schemas (`waf`, `cdn`, `challenge`, `rate_limit`) — 0.2.0
- [x] Define yari item schema (`api_endpoint`) — 0.2.0

## Schema Hardening <!-- phase:hardening -->

- [x] Offline `$ref` resolution with a bundled `referencing.Registry` (0.2.0)
- [x] Nullable optional enums (`enum` includes `null`) in every schema (0.2.0)
- [x] Recursive `None` omission in `to_dict()` (0.2.0)
- [x] `scripts/sync_schemas.py` (`--check`) + automated sync test (0.2.0)

## API Contracts <!-- phase:contracts -->

- [ ] Define inter-module REST contract conventions (finalize in ecosystem docs)
- [x] Define WebSocket streaming contracts for live analysis
- [x] Define import/export interchange formats (JSON)
- [x] Document versioning and compatibility policy

## Language Bindings <!-- phase:bindings -->

- [x] Python package for FastAPI backends (`xwa_sdk`, offline validation, `py.typed`)
- [x] Rust crate for Axum backends (`bindings/rust`, serde + optional `thiserror`) — 0.2.0
- [x] TypeScript types for Angular frontends (`xwa-sdk-types`, `prepare` build, `node:test`)
- [x] Add JSON Schema validation utilities (Python)
- [x] Cross-binding consistency: severity mapping + item models in Python/TS/Rust

## Tests & Verification <!-- phase:verification -->

- [x] Python tests: offline `$ref`, nullable enums, recursive `to_dict`, items, sync (70 tests)
- [x] TypeScript tests: type guards + `mapSeverity` (`npm test`)
- [x] Rust tests: serde roundtrip, enums, optional/`null` fields, `map_severity`
- [x] Package build verification (`uv build` wheel includes schemas + `py.typed`)
- [ ] Add CI workflow running the three suites on push

## Publishing & Adoption <!-- phase:publishing -->

- [ ] Set up package publishing pipeline (PyPI, crates.io, npm)
- [x] Create consumer examples for each language binding
- [ ] Write migration guide for existing Python modules (samurai → kensei → musha/azuma)
- [ ] Integrate xwa-sdk into samurai as first consumer
- [ ] Consume the Rust crate from shinobi/tengu (once Phase 3 of the master plan lands)
- [ ] Consume the new kabuki/yari item schemas when those apps land
- [ ] Decide the ecosystem license and add a `LICENSE` file (owner)
