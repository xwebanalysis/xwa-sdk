#!/usr/bin/env python3
"""Synchronize canonical JSON Schemas into the Python binding package.

Canonical source: ``<repo>/schemas/``
Destination:      ``<repo>/bindings/python/xwa_sdk/schemas/``

Usage::

    python scripts/sync_schemas.py          # copy canonical -> package
    python scripts/sync_schemas.py --check  # verify both trees are identical

The Python package bundles a 1:1 copy of the canonical schemas so it can
validate offline (and so wheels are self-contained). This script is the only
supported way to update the copy; ``--check`` is used by the test suite.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "schemas"
DEST_DIR = REPO_ROOT / "bindings" / "python" / "xwa_sdk" / "schemas"


def iter_schemas(root: Path) -> list[Path]:
    """Return every ``*.json`` under *root* as a sorted relative path."""
    if not root.is_dir():
        raise FileNotFoundError(f"schema directory not found: {root}")
    return sorted(path.relative_to(root) for path in root.rglob("*.json"))


def differences() -> list[str]:
    """Return human-readable differences between source and destination."""
    problems: list[str] = []
    source_files = set(iter_schemas(SOURCE_DIR))
    dest_files = set(iter_schemas(DEST_DIR)) if DEST_DIR.is_dir() else set()

    for rel in sorted(source_files - dest_files):
        problems.append(f"missing in binding: {rel}")
    for rel in sorted(dest_files - source_files):
        problems.append(f"stale in binding:   {rel}")
    for rel in sorted(source_files & dest_files):
        if not filecmp.cmp(SOURCE_DIR / rel, DEST_DIR / rel, shallow=False):
            problems.append(f"content differs:    {rel}")
    return problems


def sync() -> list[Path]:
    """Copy every canonical schema into the binding, pruning stale copies."""
    source_files = set(iter_schemas(SOURCE_DIR))
    copied: list[Path] = []

    for rel in sorted(source_files):
        src = SOURCE_DIR / rel
        dst = DEST_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or not filecmp.cmp(src, dst, shallow=False):
            shutil.copyfile(src, dst)
            copied.append(rel)

    if DEST_DIR.is_dir():
        for rel in sorted(set(iter_schemas(DEST_DIR)) - source_files):
            (DEST_DIR / rel).unlink()

    # Drop empty directories left behind after pruning stale files.
    for path in sorted(DEST_DIR.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    return copied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if the bundled copy differs from schemas/",
    )
    args = parser.parse_args(argv)

    if args.check:
        problems = differences()
        if problems:
            print("schema copies are out of sync:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            print("run: python scripts/sync_schemas.py", file=sys.stderr)
            return 1
        print(f"OK: {len(iter_schemas(SOURCE_DIR))} schemas identical in both trees")
        return 0

    copied = sync()
    if copied:
        print(f"synced {len(copied)} schema(s) into {DEST_DIR.relative_to(REPO_ROOT)}:")
        for rel in copied:
            print(f"  - {rel}")
    else:
        print("schemas already in sync; nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
