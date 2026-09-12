# Schema Reference

Canonical definitions live in `schemas/` (JSON Schema, draft 2020-12). Every schema is permissive: unknown extra properties are allowed, and optional fields are `null`-able unless stated otherwise. This keeps the layer compatible with module-specific additions.

The Python package bundles a 1:1 copy under `xwa_sdk/schemas/`; run `python scripts/sync_schemas.py` after editing the canonical files (a test enforces the copies are identical — see [versioning.md](versioning.md)).

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
| `error` | error.json | no | Failure details when `status` is ERROR. Resolved offline from the bundled copy of `error.json`. |
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
| `confidence` | string (enum) | no | `high`, `medium`, `low` or `null`. |
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

Module-specific result entities that can be attached to an analysis or streamed in `item_found` events. All follow the same style: draft 2020-12, `additionalProperties: true`, optional fields accept `null`.

| Schema | Consumed by | Required |
|--------|-------------|----------|
| `link.json` | samurai | `url` |
| `technology.json` | kensei | `category`, `name` |
| `route.json` | kensei | `path` |
| `dependency.json` | kensei | `name` |
| `waf.json` | kabuki | `vendor` |
| `cdn.json` | kabuki | `provider` |
| `challenge.json` | kabuki | `kind` |
| `rate_limit.json` | kabuki | `scope` |
| `api_endpoint.json` | yari | `protocol`, `path` |

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
| `confidence` | string (enum: high, medium, low) or null | no |
| `evidence` | string | no |

### route.json (kensei)

An SPA route discovered during profiling.

| Field | Type | Required |
|-------|------|----------|
| `path` | string | yes |
| `framework` | string (enum: angular, react, vue) or null | no |
| `route_type` | string (enum: static, lazy, guard, param) or null | no |
| `module` | string | no |

### dependency.json (kensei)

A JavaScript dependency detected from bundles or source maps.

| Field | Type | Required |
|-------|------|----------|
| `name` | string | yes |
| `version` | string | no |
| `source` | string (enum: bundle, sourcemap, inline) or null | no |
| `package_manager` | string (enum: npm, yarn, pnpm, unknown) or null | no |

### waf.json (kabuki)

A Web Application Firewall fingerprint.

| Field | Type | Required |
|-------|------|----------|
| `vendor` | string | yes |
| `product` | string or null | no |
| `confidence` | string (enum: high, medium, low) or null | no |
| `detection_method` | string (enum: header, cookie, body, status, dns, tls) or null | no |
| `evidence` | string or null | no |
| `blocked` | boolean (default false) | no |
| `severity` | string (unified severity enum) or null | no |

### cdn.json (kabuki)

A Content Delivery Network fingerprint.

| Field | Type | Required |
|-------|------|----------|
| `provider` | string | yes |
| `edge_nodes` | array of string or null | no |
| `origin_hidden` | boolean (default false) | no |
| `caching` | string (enum: hit, miss, stale, unknown) or null | no |
| `evidence` | string or null | no |

### challenge.json (kabuki)

A bot challenge or interstitial page observed while probing.

| Field | Type | Required |
|-------|------|----------|
| `kind` | string (enum: captcha, js_challenge, block_page, interstitial) | yes |
| `status_code` | integer or null | no |
| `headers` | object or null | no |
| `bypass_indicators` | array of string or null | no |
| `response_time_ms` | number or null | no |
| `severity_hint` | string (unified severity enum) or null | no |

### rate_limit.json (kabuki)

A rate limiting profile estimate.

| Field | Type | Required |
|-------|------|----------|
| `scope` | string (enum: ip, session, global, unknown) | yes |
| `limit` | integer or null | no |
| `window_seconds` | integer or null | no |
| `headers` | object or null | no |
| `threshold_estimate` | integer or null | no |
| `recommended_delay_ms` | integer or null | no |

### api_endpoint.json (yari)

An API endpoint discovered through specs, reflection or crawling.

| Field | Type | Required |
|-------|------|----------|
| `protocol` | string (enum: rest, graphql, grpc) | yes |
| `path` | string | yes |
| `method` | string or null | no |
| `host` | string or null | no |
| `params` | array of `{name, location, type, required}` or null | no |
| `auth_required` | boolean or null | no |
| `source` | string (enum: openapi, graphql_introspection, grpc_reflection, js_crawl, html) or null | no |
| `content_types` | array of string or null | no |
| `version` | string or null | no |

## Validation rules enforced by the schemas

- Enumerated fields reject unknown values (invalid `status`, `severity`, `event type`, module ids).
- Required fields must be present.
- Dates must be ISO 8601 date-time strings when `format` is declared.
- Optional enum fields accept both a valid value and `null`: they are declared as `type: ["string", "null"]` plus `enum: [..., null]`, so `null` validates and unknown values are rejected.
- Schemas referenced through `$ref` are resolved from the bundled local registry: validation never touches the network.
