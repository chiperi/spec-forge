from spec_forge.cli import app

from typer.testing import CliRunner

runner = CliRunner()


def _init(tmp_path):
    return runner.invoke(app, ["init", str(tmp_path / "proj"), "--stack", "python", "--yes"])


def test_plan_writes_plan(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["plan", str(tmp_path / "proj"), "--backend", "mock"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "proj" / "specifications" / "architecture" / "plan.md").exists()


def test_tasks_writes_tasks(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["tasks", str(tmp_path / "proj"), "--backend", "mock"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "proj" / "specifications" / "delivery" / "tasks.md").exists()


def test_validate_passes_on_fresh_bundle(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["validate", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output


def test_validate_fails_on_clarification(tmp_path):
    _init(tmp_path)
    bundle = tmp_path / "proj" / "specifications"
    spec = next((bundle / "product" / "specs").rglob("spec.md"))
    spec.write_text(spec.read_text() + "\n[NEEDS CLARIFICATION: y]\n", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(tmp_path / "proj")])
    assert result.exit_code == 1


def test_respec_diff_confirm(tmp_path):
    _init(tmp_path)
    p = str(tmp_path / "proj")
    spec_file = next((tmp_path / "proj" / "specifications" / "product" / "specs").rglob("spec.md"))

    # перша чернетка — вільний запис (фаза ще не пройдена)
    assert runner.invoke(app, ["spec", p, "--backend", "mock", "-d", "v1"]).exit_code == 0
    assert "v1" in spec_file.read_text(encoding="utf-8")

    # повторний запуск (re-spec) з відмовою → файл не змінено
    r2 = runner.invoke(app, ["spec", p, "--backend", "mock", "-d", "v2"], input="n\n")
    assert r2.exit_code == 0
    assert "v1" in spec_file.read_text(encoding="utf-8")
    assert "v2" not in spec_file.read_text(encoding="utf-8")

    # повторний запуск з --yes → перезаписано
    assert runner.invoke(app, ["spec", p, "--backend", "mock", "-d", "v3", "--yes"]).exit_code == 0
    assert "v3" in spec_file.read_text(encoding="utf-8")


def test_export_cli_writes_pdf(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["export", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output
    pdfs = list((tmp_path / "proj" / "exports").glob("*.pdf"))
    assert len(pdfs) == 1


def test_status_reflects_phases(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["status", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output
    assert "✅ init" in result.output
    assert "⬜ deploy" in result.output


def test_deploy_creates_root_and_nested_symlinks(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["deploy", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output
    root = tmp_path / "proj"
    assert (root / "AGENTS.md").is_symlink()
    assert (root / ".claude" / "agents").is_symlink()
    assert (root / ".github" / "workflows").is_symlink()
    # symlink резолвиться в specifications/
    assert (root / "AGENTS.md").resolve() == (root / "specifications" / "ai" / "AGENTS.md").resolve()
