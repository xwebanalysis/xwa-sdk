# XWA SDK Documentation

Documentation for the shared data layer of the XWA ecosystem.

| Document | Description |
|----------|-------------|
| [ADOPTION.md](ADOPTION.md) | How modules emit and consume shared data, with code examples |
| [schemas.md](schemas.md) | Field-by-field reference of every canonical schema |
| [bindings.md](bindings.md) | Language bindings: installation and usage |
| [versioning.md](versioning.md) | Versioning and compatibility policy |

## Quick orientation

- `schemas/` in the repository root holds the canonical JSON Schema definitions. They are the source of truth.
- `bindings/python/` mirrors the schemas as Python dataclasses plus validation helpers.
- `bindings/typescript/` mirrors the schemas as TypeScript types plus type guards.
- The bundled schemas inside the Python package (`xwa_sdk/schemas/`) are a 1:1 copy of the root `schemas/` directory and must be kept in sync when a schema changes.

## Core concepts

- **Analysis**: the unit of work produced by a module (scan, audit, profiling session) against a single target.
- **Finding**: a single observation, normalized to the unified severity scale.
- **Event**: streaming envelope for live results over WebSocket or message queues.
- **Error**: structured failure attached to an analysis or carried by an event.
- **Module item**: module-specific result entity (discovered link, technology, route, dependency).
