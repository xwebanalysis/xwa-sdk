"""Guarantee the bundled Python schemas stay 1:1 with the canonical tree.

Also exercises ``scripts/sync_schemas.py`` (both ``--check`` outcomes) so the
tool used to keep the copies in sync is itself covered.
"""

from __future__ import annotations

import filecmp
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import xwa_sdk

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_DIR = REPO_ROOT / "schemas"
BUNDLED_DIR = Path(xwa_sdk.__file__).parent / "schemas"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_schemas.py"


def _relative_json(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*.json"))


def test_bundled_schema_set_matches_canonical():
    canonical = set(_relative_json(CANONICAL_DIR))
    bundled = set(_relative_json(BUNDLED_DIR))
    assert canonical == bundled, "schema trees differ; run scripts/sync_schemas.py"
    for rel in sorted(canonical):
        assert filecmp.cmp(CANONICAL_DIR / rel, BUNDLED_DIR / rel, shallow=False), (
            f"schema copy differs: {rel}; run scripts/sync_schemas.py"
        )


@pytest.mark.parametrize("rel", _relative_json(BUNDLED_DIR), ids=str)
def test_every_schema_is_valid_draft202012(rel: Path):
    schema = json.loads((BUNDLED_DIR / rel).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_all_schemas_declare_remote_ids_under_the_same_prefix():
    ids = set()
    for rel in _relative_json(BUNDLED_DIR):
        schema = json.loads((BUNDLED_DIR / rel).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        ids.add(schema["$id"])
    assert len(ids) == len(_relative_json(BUNDLED_DIR)), "duplicate $id values"
    assert all(i.startswith("https://github.com/xwebanalysis/xwa-sdk/schemas/") for i in ids)


def test_all_item_schemas_are_bundled():
    expected = {
        "link.json",
        "technology.json",
        "route.json",
        "dependency.json",
        "waf.json",
        "cdn.json",
        "challenge.json",
        "rate_limit.json",
        "api_endpoint.json",
    }
    bundled_items = {path.name for path in (BUNDLED_DIR / "items").glob("*.json")}
    assert expected <= bundled_items


def _load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_schemas", SYNC_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sync_script_check_passes(capsys):
    module = _load_sync_module()
    assert module.main(["--check"]) == 0
    assert "identical" in capsys.readouterr().out


def test_sync_script_check_detects_drift(tmp_path, monkeypatch, capsys):
    module = _load_sync_module()
    monkeypatch.setattr(module, "DEST_DIR", tmp_path / "schemas")  # empty destination
    assert module.main(["--check"]) == 1
    assert "out of sync" in capsys.readouterr().err
