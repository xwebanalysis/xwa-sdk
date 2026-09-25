# Changelog

All notable changes to the XWA SDK are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) (simplified).
Version numbers follow the [versioning policy](docs/versioning.md).

> **License note (owner decision pending):** the Python, TypeScript and Rust
> bindings declare `MIT` in their package metadata because the build tooling
> requires a value. The XWA ecosystem owner has not published an ecosystem-wide
> `LICENSE` file, so the license is **not final** — the metadata is a
> placeholder, not a grant. Do not add a `LICENSE` file until the owner decides.

## [0.2.1] - 2026-09-25

### Changed

- Version bumped to `0.2.1` in `pyproject.toml`, `package.json` (and
  lockfile), the crate manifest and `xwa_sdk.__version__` — a metadata-only
  release so consumers pick up a fresh build.
- Verified bindings across Python 3.14 / TypeScript 5 / Rust 1.96; no schema
  changes. Consumer imports (`Event`, `to_dict`, `Error`) confirmed compatible.

## [0.2.0] - 2026-09-12

### Fixed

- Python validation is now fully offline: a local `referencing.Registry` maps
  every bundled schema `$id`, so relative `$ref`s (for example
  `analysis.json` → `error.json`) resolve without network access.
- `validate_*` helpers always raise `jsonschema.exceptions.ValidationError`;
  referencing failures no longer leak as `_WrappedReferencingError`.
  `is_valid_*` predicates return a plain `bool` for any reference problem.
- Optional enum fields (`finding.confidence`, `technology.confidence`,
  `route.framework`, `route.route_type`, `dependency.source`,
  `dependency.package_manager` and the new items) now accept `null` as
  documented, while still rejecting unknown values.
- `to_dict()` now omits `None` recursively (nested dicts, lists and dataclass
  fields), not just at the top level.
- TypeScript `mapSeverity` only translates tool-specific names for their own
  tool (`tengu`), matching the Python implementation.

### Added

- New item schemas (root `schemas/items/` and the bundled Python copy):
  `waf.json`, `cdn.json`, `challenge.json`, `rate_limit.json` (kabuki) and
  `api_endpoint.json` (yari).
- Python dataclasses `Waf`, `Cdn`, `Challenge`, `RateLimit`, `ApiEndpoint` with
  `to_dict`/`from_dict` support, plus `ITEM_KINDS` and `is_valid_error` /
  `is_valid_item` helpers.
- Rust binding `bindings/rust` (crate `xwa-sdk`, edition 2021): serde models
  for `Analysis`, `Finding`, `Error`, `Summary`, `Event`, every module item and
  `map_severity`, with optional `thiserror` support.
- `scripts/sync_schemas.py` (`--check` mode) plus a test that guarantees the
  bundled Python schemas are identical to the canonical tree.
- TypeScript: `prepare`/`prepublishOnly` scripts, `exports`/`types`/
  `repository`/`files` metadata, types + type guards for the new items and a
  `node:test` suite (`npm test`).
- Python packaging: `py.typed` marker, PEP 639 `license = "MIT"`, modern
  `license-files`-free metadata and a `test` optional-dependency extra.
- New Python tests (offline `$ref`, nullable enums, recursive `to_dict`,
  roundtrips, the five new items, schema sync, `map_severity`): 70 tests.

### Changed

- Version bumped to `0.2.0` in `pyproject.toml`, `package.json` (and lockfile),
  the crate manifest and `xwa_sdk.__version__`.
- `docs/` updated: schema reference tables for the new items, Rust binding
  guide, adoption examples for kabuki/yari and the schema sync workflow.

## [0.1.0] - 2026-08-08

### Added

- Canonical JSON Schemas (draft 2020-12): `analysis.json`, `finding.json`,
  `event.json`, `error.json` and items `link.json`, `technology.json`,
  `route.json`, `dependency.json`.
- Python binding `xwa_sdk`: dataclasses, `to_dict`/`from_dict`,
  `map_severity`, bundled schemas and `jsonschema` validation helpers.
- TypeScript binding `xwa-sdk-types`: shared types, type guards and
  `mapSeverity`.
- Documentation: `docs/ADOPTION.md`, `docs/schemas.md`, `docs/bindings.md`,
  `docs/versioning.md`.
