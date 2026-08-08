# Schema Reference

Canonical definitions live in `schemas/` (JSON Schema, draft 2020-12). Every schema is permissive: unknown extra properties are allowed, and optional fields are `null`-able unless stated otherwise. This keeps the layer compatible with module-specific additions.

## analysis.json

Top-level unit of work produced by an XWA tool. Mirrors what samurai calls a `Scan` and what kensei calls a `Profile`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Module-specific identifier of the analysis (scan or profile id). |
| `tool` | string (enum) | yes | Producing module: samurai, shinobi, tengu, kensei, kabuki, yari, musha, azuma. |
| `tool_version` | string | no | Version of the producing module. |
| `target` | string | yes | Analyzed target: domain, URL or host. |
| `status` | string (enum) | yes | Lifecycle: PENDING, RUNNING, COMPLETED, ERROR, CANCELLED. |
| `analysis_type` | string | no | Module-specific kind, e.g. `port_scan`, `crawler`, `audit`, `profile`. |
| `created_at` | string (date-time) | yes | Creation timestamp. |
| `started_at` | string (date-time) | no | When execution began. |
| `finished_at` | string (date-time) | no | When execution reached a terminal state. |
| `error` | error.json | no | Failure details when `status` is ERROR. |
| `summary` | object | no | Aggregated counts: `total_items`, `by_severity`, `by_category`. |

## finding.json

A single observation mapped to the unified severity scale.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | no | Assigned when persisted. |
| `tool` | string (enum) | yes | Producing module. |
| `severity` | string (enum) | yes | Unified scale: pass, info, low, medium, high, critical. See ADOPTION.md for per-module mapping. |
| `category` | string | no | Module-specific group. samurai: finding_type. tengu: performance, seo, a11y, best_practices. kensei: technology category. |
| `check` | string | no | Module-specific sub-type or check identifier. |
| `title` | string | yes | Short human-readable title. |
| `description` | string | yes | Detailed explanation. |
| `target_url` | string (uri) | no | URL or resource the finding refers to. |
| `evidence` | object | no | Proof, module-specific: `snippet`, `poc_payload`, `data`. |
| `cvss_score` | string | no | CVSS score kept as string to preserve precision. |
| `confidence` | string (enum) | no | high, medium, low. |
| `detected_at` | string (date-time) | no | When the finding was observed. |

## event.json

Streaming envelope for live analysis progress.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `seq` | integer | yes | Monotonic sequence number scoped to the analysis stream. |
| `type` | string (enum) | yes | analysis_started, analysis_progress, item_found, analysis_completed, analysis_error, log. |
| `tool` | string (enum) | yes | Producing module. |
| `analysis_id` | string | yes | Analysis this event belongs to. |
| `ts` | string (date-time) | yes | Event timestamp. |
| `payload` | object | no | Event-specific data. For `item_found`: a finding or module item. For `analysis_progress`: `{ percent?, message? }`. For `analysis_error`: an error object. |

## error.json

Unified failure envelope.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | yes | Stable machine-readable code, e.g. NETWORK_ERROR, TIMEOUT, INVALID_TARGET, INTERNAL. |
| `message` | string | yes | Human-readable description. |
| `detail` | object | no | Structured context, module-specific. |
| `retryable` | boolean | no | Whether retrying the operation may succeed (default false). |

## Module items (`schemas/items/`)

Module-specific result entities that can be attached to an analysis or streamed in `item_found` events.

### link.json (samurai)

A link discovered while crawling.

| Field | Type | Required |
|-------|------|----------|
| `url` | string (uri) | yes |
| `status_code` | integer | no |
| `content_type` | string | no |

### technology.json (kensei)

A detected technology stack component.

| Field | Type | Required |
|-------|------|----------|
| `category` | string (enum: frontend, backend, cdn, analytics, hosting) | yes |
| `name` | string | yes |
| `version` | string | no |
| `confidence` | string (enum: high, medium, low) | no |
| `evidence` | string | no |

### route.json (kensei)

An SPA route discovered during profiling.

| Field | Type | Required |
|-------|------|----------|
| `path` | string | yes |
| `framework` | string (enum: angular, react, vue) | no |
| `route_type` | string (enum: static, lazy, guard, param) | no |
| `module` | string | no |

### dependency.json (kensei)

A JavaScript dependency detected from bundles or source maps.

| Field | Type | Required |
|-------|------|----------|
| `name` | string | yes |
| `version` | string | no |
| `source` | string (enum: bundle, sourcemap, inline) | no |
| `package_manager` | string (enum: npm, yarn, pnpm, unknown) | no |

## Validation rules enforced by the schemas

- Enumerated fields reject unknown values (invalid `status`, `severity`, `event type`, module ids).
- Required fields must be present.
- Dates must be ISO 8601 date-time strings when `format` is declared.
- Optional enum fields accept both a valid value and `null` (they are declared as `type: ["string", "null"]` with an `anyOf` enum constraint).
