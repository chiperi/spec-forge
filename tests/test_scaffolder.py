from spec_forge.profiles import get_profile
from spec_forge.scaffolder import BundleExistsError, scaffold

import pytest


def _ctx() -> dict:
    return {"project": "demo", "summary": "s", **get_profile("python").render_context()}


def test_scaffold_creates_bundle(tmp_path):
    written = scaffold(tmp_path, _ctx())
    assert (tmp_path / "specifications" / "ai" / "AGENTS.md").exists()
    assert any(w.endswith("spec.md") for w in written)


def test_scaffold_order_is_deterministic(tmp_path):
    written = scaffold(tmp_path, _ctx())
    assert written == sorted(written)


def test_scaffold_is_reproducible(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    scaffold(a, _ctx())
    scaffold(b, _ctx())
    fa = (a / "specifications" / "ai" / "AGENTS.md").read_text(encoding="utf-8")
    fb = (b / "specifications" / "ai" / "AGENTS.md").read_text(encoding="utf-8")
    assert fa == fb


def test_scaffold_guards_existing(tmp_path):
    scaffold(tmp_path, _ctx())
    with pytest.raises(BundleExistsError):
        scaffold(tmp_path, _ctx())
