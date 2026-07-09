from spec_forge.export_pdf import export_bundle
from spec_forge.profiles import get_profile
from spec_forge.scaffolder import scaffold

import pytest


def _ctx() -> dict:
    return {"project": "demo", "summary": "s", **get_profile("python").render_context()}


def test_export_creates_timestamped_pdf(tmp_path):
    scaffold(tmp_path, _ctx())
    out = export_bundle(tmp_path)
    assert out.exists()
    assert out.parent.name == "exports"
    assert out.name.startswith("spec-forge-export-")
    assert out.suffix == ".pdf"
    assert out.read_bytes()[:4] == b"%PDF"


def test_export_missing_bundle_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_bundle(tmp_path)
