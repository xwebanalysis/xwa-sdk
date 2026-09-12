/**
 * XWA SDK — shared TypeScript types and helpers for the XWA ecosystem.
 * Mirrors the canonical JSON Schemas in xwa-sdk/schemas. Zero dependencies.
 */

export const TOOLS = [
  "samurai",
  "shinobi",
  "tengu",
  "kensei",
  "kabuki",
  "yari",
  "musha",
  "azuma",
] as const;
export type Tool = (typeof TOOLS)[number];

export const ANALYSIS_STATUS = [
  "PENDING",
  "RUNNING",
  "COMPLETED",
  "ERROR",
  "CANCELLED",
] as const;
export type AnalysisStatus = (typeof ANALYSIS_STATUS)[number];

export const SEVERITIES = [
  "pass",
  "info",
  "low",
  "medium",
  "high",
  "critical",
] as const;
export type Severity = (typeof SEVERITIES)[number];

export const EVENT_TYPES = [
  "analysis_started",
  "analysis_progress",
  "item_found",
  "analysis_completed",
  "analysis_error",
  "log",
] as const;
export type EventType = (typeof EVENT_TYPES)[number];

/** Detection confidence (shared by finding/technology/waf). */
export type Confidence = "high" | "medium" | "low";

export const DETECTION_METHODS = ["header", "cookie", "body", "status", "dns", "tls"] as const;
export type DetectionMethod = (typeof DETECTION_METHODS)[number];

export const CACHING_STATES = ["hit", "miss", "stale", "unknown"] as const;
export type Caching = (typeof CACHING_STATES)[number];

export const CHALLENGE_KINDS = [
  "captcha",
  "js_challenge",
  "block_page",
  "interstitial",
] as const;
export type ChallengeKind = (typeof CHALLENGE_KINDS)[number];

export const RATE_LIMIT_SCOPES = ["ip", "session", "global", "unknown"] as const;
export type RateLimitScope = (typeof RATE_LIMIT_SCOPES)[number];

export const API_PROTOCOLS = ["rest", "graphql", "grpc"] as const;
export type ApiProtocol = (typeof API_PROTOCOLS)[number];

export const DISCOVERY_SOURCES = [
  "openapi",
  "graphql_introspection",
  "grpc_reflection",
  "js_crawl",
  "html",
] as const;
export type DiscoverySource = (typeof DISCOVERY_SOURCES)[number];

export interface ErrorInfo {
  code: string;
  message: string;
  detail?: Record<string, unknown> | null;
  retryable?: boolean;
}

export interface Summary {
  total_items?: number | null;
  by_severity?: Record<string, number>;
  by_category?: Record<string, number>;
}

export interface Analysis {
  id: string;
  tool: Tool;
  target: string;
  status: AnalysisStatus;
  created_at: string;
  tool_version?: string | null;
  analysis_type?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  error?: ErrorInfo | null;
  summary?: Summary | null;
}

export interface Finding {
  tool: Tool;
  severity: Severity;
  title: string;
  description: string;
  id?: string | null;
  category?: string | null;
  check?: string | null;
  target_url?: string | null;
  evidence?: Record<string, unknown> | null;
  cvss_score?: string | null;
  confidence?: Confidence | null;
  detected_at?: string | null;
}

export interface Event {
  seq: number;
  type: EventType;
  tool: Tool;
  analysis_id: string;
  ts: string;
  payload?: unknown;
}

export interface DiscoveredLink {
  url: string;
  status_code?: number | null;
  content_type?: string | null;
}

export interface Technology {
  category: "frontend" | "backend" | "cdn" | "analytics" | "hosting";
  name: string;
  version?: string | null;
  confidence?: Confidence | null;
  evidence?: string | null;
}

export interface DiscoveredRoute {
  path: string;
  framework?: "angular" | "react" | "vue" | null;
  route_type?: "static" | "lazy" | "guard" | "param" | null;
  module?: string | null;
}

export interface JsDependency {
  name: string;
  version?: string | null;
  source?: "bundle" | "sourcemap" | "inline" | null;
  package_manager?: "npm" | "yarn" | "pnpm" | "unknown" | null;
}

// ── kabuki / yari module items ──────────────────────────────────────────────

/** kabuki: Web Application Firewall fingerprint. */
export interface Waf {
  vendor: string;
  product?: string | null;
  confidence?: Confidence | null;
  detection_method?: DetectionMethod | null;
  evidence?: string | null;
  blocked?: boolean;
  severity?: Severity | null;
}

/** kabuki: Content Delivery Network fingerprint. */
export interface Cdn {
  provider: string;
  edge_nodes?: string[] | null;
  origin_hidden?: boolean;
  caching?: Caching | null;
  evidence?: string | null;
}

/** kabuki: bot challenge or interstitial page. */
export interface Challenge {
  kind: ChallengeKind;
  status_code?: number | null;
  headers?: Record<string, unknown> | null;
  bypass_indicators?: string[] | null;
  response_time_ms?: number | null;
  severity_hint?: Severity | null;
}

/** kabuki: rate limiting profile estimate. */
export interface RateLimit {
  scope: RateLimitScope;
  limit?: number | null;
  window_seconds?: number | null;
  headers?: Record<string, unknown> | null;
  threshold_estimate?: number | null;
  recommended_delay_ms?: number | null;
}

/** yari: discovered API parameter. */
export interface ApiParam {
  name: string;
  location?: string | null;
  type?: string | null;
  required?: boolean | null;
}

/** yari: API endpoint discovered through specs, reflection or crawling. */
export interface ApiEndpoint {
  protocol: ApiProtocol;
  path: string;
  method?: string | null;
  host?: string | null;
  params?: ApiParam[] | null;
  auth_required?: boolean | null;
  source?: DiscoverySource | null;
  content_types?: string[] | null;
  version?: string | null;
}

// ── Severity mapping ────────────────────────────────────────────────────────

const TENGU_SEVERITY_MAP: Record<string, Severity> = {
  Pass: "pass",
  Info: "info",
  Warning: "medium",
  Error: "high",
};

/**
 * Map a module-internal severity to the unified scale. Mirrors the Python
 * `map_severity`: module-specific names are only translated for their own
 * tool (`tengu`), otherwise an already-unified value passes through.
 */
export function mapSeverity(tool: Tool, severity: string): Severity {
  if (tool === "tengu") {
    const mapped = TENGU_SEVERITY_MAP[severity];
    if (mapped) {
      return mapped;
    }
  }
  if ((SEVERITIES as readonly string[]).includes(severity)) {
    return severity as Severity;
  }
  throw new Error(`Unknown severity '${severity}' for tool '${tool}'`);
}

// ── Type guards ─────────────────────────────────────────────────────────────

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isMember<T extends readonly string[]>(list: T, value: unknown): value is T[number] {
  return typeof value === "string" && (list as readonly string[]).includes(value);
}

export function isAnalysis(value: unknown): value is Analysis {
  if (!isRecord(value)) {
    return false;
  }
  return (
    typeof value.id === "string" &&
    isMember(TOOLS, value.tool) &&
    typeof value.target === "string" &&
    isMember(ANALYSIS_STATUS, value.status) &&
    typeof value.created_at === "string"
  );
}

export function isFinding(value: unknown): value is Finding {
  if (!isRecord(value)) {
    return false;
  }
  return (
    isMember(TOOLS, value.tool) &&
    isMember(SEVERITIES, value.severity) &&
    typeof value.title === "string" &&
    typeof value.description === "string"
  );
}

export function isEvent(value: unknown): value is Event {
  if (!isRecord(value)) {
    return false;
  }
  return (
    typeof value.seq === "number" &&
    isMember(EVENT_TYPES, value.type) &&
    isMember(TOOLS, value.tool) &&
    typeof value.analysis_id === "string" &&
    typeof value.ts === "string"
  );
}

export function isWaf(value: unknown): value is Waf {
  return isRecord(value) && typeof value.vendor === "string";
}

export function isCdn(value: unknown): value is Cdn {
  return isRecord(value) && typeof value.provider === "string";
}

export function isChallenge(value: unknown): value is Challenge {
  return isRecord(value) && isMember(CHALLENGE_KINDS, value.kind);
}

export function isRateLimit(value: unknown): value is RateLimit {
  return isRecord(value) && isMember(RATE_LIMIT_SCOPES, value.scope);
}

export function isApiEndpoint(value: unknown): value is ApiEndpoint {
  return (
    isRecord(value) && isMember(API_PROTOCOLS, value.protocol) && typeof value.path === "string"
  );
}
