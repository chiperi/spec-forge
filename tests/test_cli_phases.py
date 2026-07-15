from spec_forge.cli import app

from typer.testing import CliRunner

runner = CliRunner()


def _init(tmp_path):
    return runner.invoke(app, ["init", str(tmp_path / "proj"), "--stack", "python", "--yes"])


def test_plan_writes_plan(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["plan", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "proj" / "specifications" / "architecture" / "plan.md").exists()


def test_tasks_writes_tasks(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["tasks", str(tmp_path / "proj")])
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

    # first draft — free write (the phase has not been passed yet)
    assert runner.invoke(app, ["spec", p, "-d", "v1"]).exit_code == 0
    assert "v1" in spec_file.read_text(encoding="utf-8")

    # re-run (re-spec) with a decline → file unchanged
    r2 = runner.invoke(app, ["spec", p, "-d", "v2"], input="n\n")
    assert r2.exit_code == 0
    assert "v1" in spec_file.read_text(encoding="utf-8")
    assert "v2" not in spec_file.read_text(encoding="utf-8")

    # re-run with --yes → overwritten
    assert runner.invoke(app, ["spec", p, "-d", "v3", "--yes"]).exit_code == 0
    assert "v3" in spec_file.read_text(encoding="utf-8")


def test_export_cli_writes_pdf(tmp_path):
    _init(tmp_path)
    result = runner.invoke(app, ["export", str(tmp_path / "proj")])
    assert result.exit_code == 0, result.output
    pdfs = list((tmp_path / "proj" / "exports").glob("*.pdf"))
    assert len(pdfs) == 1


def test_command_install_uninstall_cli(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r1 = runner.invoke(app, ["command", "install", "--project"])
    assert r1.exit_code == 0, r1.output
    wrapper = tmp_path / ".claude" / "commands" / "spec-forge.md"
    agents = tmp_path / ".claude" / "agents"
    assert wrapper.exists()
    assert (agents / "business-analyst.md").exists()
    assert (agents / "reverse-analyst.md").exists()
    assert len(list(agents.glob("*.md"))) == 6
    r2 = runner.invoke(app, ["command", "uninstall", "--project"])
    assert r2.exit_code == 0
    assert not wrapper.exists()
    assert not (agents / "business-analyst.md").exists()


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
    # symlink resolves into specifications/
    assert (root / "AGENTS.md").resolve() == (root / "specifications" / "ai" / "AGENTS.md").resolve()
