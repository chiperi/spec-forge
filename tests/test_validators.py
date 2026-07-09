from spec_forge.profiles import get_profile
from spec_forge.scaffolder import scaffold
from spec_forge.validators import validate_bundle


def _ctx() -> dict:
    return {"project": "demo", "summary": "s", **get_profile("python").render_context()}


def _bundle(tmp_path):
    scaffold(tmp_path, _ctx())
    return tmp_path / "specifications"


def test_fresh_bundle_passes_all_gates(tmp_path):
    results = validate_bundle(_bundle(tmp_path))
    failed = [r.gate for r in results if not r.passed]
    assert not failed, failed


def test_clarification_gate_fails(tmp_path):
    bundle = _bundle(tmp_path)
    spec = next((bundle / "product" / "specs").rglob("spec.md"))
    spec.write_text(spec.read_text() + "\n[NEEDS CLARIFICATION: open]\n", encoding="utf-8")
    by_gate = {r.gate: r for r in validate_bundle(bundle)}
    assert not by_gate["clarifications"].passed


def test_structure_gate_fails_without_plan(tmp_path):
    bundle = _bundle(tmp_path)
    (bundle / "architecture" / "plan.md").unlink()
    by_gate = {r.gate: r for r in validate_bundle(bundle)}
    assert not by_gate["structure"].passed
