# xwa-sdk-types — TypeScript bindings

Shared types, type guards and severity mapping for the XWA ecosystem. Mirrors
the canonical JSON Schemas in `xwa-sdk/schemas`. Zero runtime dependencies.

```bash
npm install
npm run build   # compiles to dist/ (types + declarations)
npm test        # builds then runs node:test
```

```ts
import { Analysis, Finding, isFinding, mapSeverity } from "xwa-sdk-types";

const severity = mapSeverity("tengu", "Warning"); // "medium"

if (isFinding(payload)) {
  payload.severity; // typed as Severity
}
```

Includes types and guards for the module items: `DiscoveredLink`,
`Technology`, `DiscoveredRoute`, `JsDependency`, `Waf`, `Cdn`, `Challenge`,
`RateLimit`, `ApiEndpoint` (`isWaf`, `isCdn`, `isChallenge`, `isRateLimit`,
`isApiEndpoint`).
