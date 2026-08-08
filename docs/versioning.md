# Versioning Policy

## Schemas

- The schema set is versioned as a whole under `0.x` until the first stable release.
- **Breaking changes** (removing a required field, changing a type, narrowing an enum) bump the minor version: `0.1.0` -> `0.2.0`.
- **Additive changes** (new optional fields, new module item schemas) bump the patch: `0.1.0` -> `0.1.1`.
- Module item schemas may evolve independently but follow the same rule applied to the set.

## Bindings

- Bindings are versioned in lockstep with the schema set. A binding release is expected to validate against the schemas of the same version.
- A module consuming a binding declares the SDK version it was validated against in the `tool_version` field of its analyses.

## Compatibility guarantees

- Consumers must treat unknown extra properties as forward-compatible by design; the schemas allow `additionalProperties`.
- Enum values are never removed without a minor bump; a deprecated value is kept until the next minor.
- `0.x` does not guarantee wire stability across minors; modules should pin the SDK version they consume.

## Changing a schema

1. Edit the canonical file under `schemas/`.
2. Copy the changed file into `bindings/python/xwa_sdk/schemas/` (the package bundles a 1:1 copy).
3. Update the corresponding binding types (Python dataclasses and/or TypeScript interfaces).
4. Bump the SDK version according to this policy.
5. Update `docs/schemas.md` and the tests.
