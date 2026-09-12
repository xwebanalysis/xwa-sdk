"use strict";

/**
 * Tests for the TypeScript binding: type guards and severity mapping.
 * Run with `npm test` (builds `dist/` first, then `node --test`).
 */

const test = require("node:test");
const assert = require("node:assert/strict");

const {
  ANALYSIS_STATUS,
  TOOLS,
  mapSeverity,
  isAnalysis,
  isFinding,
  isEvent,
  isWaf,
  isCdn,
  isChallenge,
  isRateLimit,
  isApiEndpoint,
} = require("../dist/index.js");

test("mapSeverity mirrors the Python binding", () => {
  assert.equal(mapSeverity("tengu", "Pass"), "pass");
  assert.equal(mapSeverity("tengu", "Info"), "info");
  assert.equal(mapSeverity("tengu", "Warning"), "medium");
  assert.equal(mapSeverity("tengu", "Error"), "high");
  assert.equal(mapSeverity("samurai", "critical"), "critical");
  assert.equal(mapSeverity("kensei", "low"), "low");
  // Module-specific names are only translated for their own tool.
  assert.throws(() => mapSeverity("samurai", "Warning"), /Unknown severity 'Warning' for tool 'samurai'/);
  assert.throws(() => mapSeverity("tengu", "bogus"), /Unknown severity/);
});

test("isAnalysis narrows valid analyses and rejects bad payloads", () => {
  const analysis = {
    id: "a1",
    tool: "samurai",
    target: "https://example.com",
    status: "RUNNING",
    created_at: "2026-08-08T10:00:00Z",
  };
  assert.equal(isAnalysis(analysis), true);
  assert.equal(isAnalysis({ ...analysis, status: "PAUSED" }), false);
  assert.equal(isAnalysis({ ...analysis, tool: "unknown" }), false);
  assert.equal(isAnalysis(null), false);
  assert.equal(isAnalysis("analysis"), false);
});

test("isFinding and isEvent validate required fields and enums", () => {
  assert.equal(
    isFinding({ tool: "tengu", severity: "medium", title: "t", description: "d" }),
    true,
  );
  assert.equal(
    isFinding({ tool: "tengu", severity: "urgent", title: "t", description: "d" }),
    false,
  );
  assert.equal(
    isEvent({
      seq: 1,
      type: "item_found",
      tool: "kabuki",
      analysis_id: "a1",
      ts: "2026-08-08T10:00:01Z",
    }),
    true,
  );
  assert.equal(
    isEvent({
      seq: "1",
      type: "item_found",
      tool: "kabuki",
      analysis_id: "a1",
      ts: "2026-08-08T10:00:01Z",
    }),
    false,
  );
});

test("new item type guards accept valid payloads with null optional enums", () => {
  assert.equal(isWaf({ vendor: "Cloudflare", confidence: null, severity: null }), true);
  assert.equal(isWaf({ confidence: "high" }), false);
  assert.equal(isCdn({ provider: "Fastly", edge_nodes: null, caching: null }), true);
  assert.equal(isCdn({ provider: 1 }), false);
  assert.equal(isChallenge({ kind: "js_challenge", status_code: null }), true);
  assert.equal(isChallenge({ kind: "quiz" }), false);
  assert.equal(isRateLimit({ scope: "ip", limit: null }), true);
  assert.equal(isRateLimit({ scope: "galaxy" }), false);
  assert.equal(
    isApiEndpoint({ protocol: "rest", path: "/v1/users", auth_required: null, source: null }),
    true,
  );
  assert.equal(isApiEndpoint({ protocol: "soap", path: "/v1/users" }), false);
  assert.equal(isApiEndpoint({ protocol: "rest" }), false);
});

test("exported constants stay in lockstep with the schemas", () => {
  assert.deepEqual(TOOLS, [
    "samurai",
    "shinobi",
    "tengu",
    "kensei",
    "kabuki",
    "yari",
    "musha",
    "azuma",
  ]);
  assert.deepEqual(ANALYSIS_STATUS, ["PENDING", "RUNNING", "COMPLETED", "ERROR", "CANCELLED"]);
});
