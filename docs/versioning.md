# Versioning Policy

## Schemas

- The schema set is versioned as a whole under `0.x` until the first stable release.
- **Breaking changes** (removing a required field, changing a type, narrowing an enum) bump the minor version: `0.1.0` -> `0.2.0`.
- **Additive changes** (new optional fields, new module item schemas) bump the patch: `0.1.0` -> `0.1.1`.
- Module item schemas may evolve independently but follow the same rule applied to the set.
- Every release is recorded in [CHANGELOG.md](../CHANGELOG.md).

Examples:

- `0.2.0` — added the kabuki/yari item schemas and fixed nullable enums and
  offline `$ref` resolution (behavioral fixes plus additive items).
- `0.1.1` (hypothetical) — adding one optional field to `finding.json` without
  changing existing semantics.

## Bindings

- Bindings are versioned in lockstep with the schema set. A binding release is expected to validate against the schemas of the same version.
- A module consuming a binding declares the SDK version it was validated against in the `tool_version` field of its analyses.
- Python, TypeScript and Rust carry the same version number; `xwa_sdk.__version__` is checked by the test suite.

## Compatibility guarantees

- Consumers must treat unknown extra properties as forward-compatible by design; the schemas allow `additionalProperties`.
- Enum values are never removed without a minor bump; a deprecated value is kept until the next minor.
- `0.x` does not guarantee wire stability across minors; modules should pin the SDK version they consume.

## Changing a schema

1. Edit the canonical file under `schemas/` (source of truth).
2. Synchronize the bundled Python copy — never edit it by hand:
   ```bash
   python scripts/sync_schemas.py          # copy canonical -> xwa_sdk/schemas/
   python scripts/sync_schemas.py --check  # verify; exits 1 if the trees drift
   ```
3. Update the corresponding binding types: Python dataclasses in
   `bindings/python/xwa_sdk/models.py`, TypeScript interfaces in
   `bindings/typescript/src/index.ts`, Rust structs in
   `bindings/rust/src/lib.rs`.
4. Bump the version everywhere — `bindings/python/pyproject.toml`,
   `bindings/typescript/package.json` (+ lockfile), `bindings/rust/Cargo.toml`
   and `xwa_sdk.__version__` — according to this policy.
5. Update `docs/schemas.md`, `docs/bindings.md` and the tests.

### Automated enforcement

- `bindings/python/tests/test_schemas_sync.py` compares the two schema trees
  file-by-file (presence and content) and exercises the sync script.
- Run `python scripts/sync_schemas.py --check` in CI before packaging so a
  stale bundled copy can never ship.
- The Python suite (`pytest -q`), TypeScript suite (`npm test`) and Rust suite
  (`cargo test`) must pass before a release; all three are expected to be run
  for a version bump.
