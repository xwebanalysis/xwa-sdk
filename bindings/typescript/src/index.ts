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
  confidence?: "high" | "medium" | "low" | null;
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
  confidence?: "high" | "medium" | "low" | null;
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

// ── Severity mapping ────────────────────────────────────────────────────────

const MODULE_SEVERITY_MAP: Record<string, Severity> = {
  Pass: "pass",
  Info: "info",
  Warning: "medium",
  Error: "high",
};

export function mapSeverity(tool: Tool, severity: string): Severity {
  const mapped = MODULE_SEVERITY_MAP[severity];
  if (mapped) {
    return mapped;
  }
  if ((SEVERITIES as readonly string[]).includes(severity)) {
    return severity as Severity;
  }
  throw new Error(`Unknown severity '${severity}' for tool '${tool}'`);
}

// ── Type guards ─────────────────────────────────────────────────────────────

export function isAnalysis(value: unknown): value is Analysis {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "string" &&
    typeof v.tool === "string" &&
    (TOOLS as readonly string[]).includes(v.tool) &&
    typeof v.target === "string" &&
    typeof v.status === "string" &&
    (ANALYSIS_STATUS as readonly string[]).includes(v.status) &&
    typeof v.created_at === "string"
  );
}

export function isFinding(value: unknown): value is Finding {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const v = value as Record<string, unknown>;
  return (
    typeof v.tool === "string" &&
    (TOOLS as readonly string[]).includes(v.tool) &&
    typeof v.severity === "string" &&
    (SEVERITIES as readonly string[]).includes(v.severity) &&
    typeof v.title === "string" &&
    typeof v.description === "string"
  );
}

export function isEvent(value: unknown): value is Event {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const v = value as Record<string, unknown>;
  return (
    typeof v.seq === "number" &&
    typeof v.type === "string" &&
    (EVENT_TYPES as readonly string[]).includes(v.type) &&
    typeof v.tool === "string" &&
    (TOOLS as readonly string[]).includes(v.tool) &&
    typeof v.analysis_id === "string" &&
    typeof v.ts === "string"
  );
}
