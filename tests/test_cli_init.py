from spec_forge.cli import app

from typer.testing import CliRunner

runner = CliRunner()


def test_init_yes_creates_bundle(tmp_path):
    target = tmp_path / "proj"
    result = runner.invoke(app, ["init", str(target), "--stack", "python", "--yes"])
    assert result.exit_code == 0, result.output
    assert (target / "specifications" / "ai" / "AGENTS.md").exists()


def test_init_rejects_unknown_stack(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path / "p"), "--stack", "cobol", "--yes"])
    assert result.exit_code != 0


def test_init_guards_existing_bundle(tmp_path):
    target = tmp_path / "proj"
    runner.invoke(app, ["init", str(target), "--stack", "python", "--yes"])
    result = runner.invoke(app, ["init", str(target), "--stack", "python", "--yes"])
    assert result.exit_code == 1


def test_spec_requires_bundle(tmp_path):
    result = runner.invoke(app, ["spec", str(tmp_path)])
    assert result.exit_code == 1


def test_spec_writes_draft(tmp_path):
    target = tmp_path / "proj"
    runner.invoke(app, ["init", str(target), "--stack", "python", "--yes"])
    result = runner.invoke(app, ["spec", str(target)])
    assert result.exit_code == 0, result.output
    assert (target / "specifications" / "product" / "specs" / "001-feature" / "spec.md").exists()


def test_design_writes_draft(tmp_path):
    target = tmp_path / "proj"
    runner.invoke(app, ["init", str(target), "--stack", "python", "--yes"])
    result = runner.invoke(app, ["design", str(target)])
    assert result.exit_code == 0, result.output
    assert (target / "specifications" / "design" / "feature.design.md").exists()
