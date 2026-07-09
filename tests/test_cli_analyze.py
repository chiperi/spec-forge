from spec_forge.cli import app

from typer.testing import CliRunner

runner = CliRunner()


def _src(tmp_path):
    src = tmp_path / "app"
    (src / "src").mkdir(parents=True)
    (src / "src" / "main.py").write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    return src


def test_analyze_both(tmp_path):
    src = _src(tmp_path)
    result = runner.invoke(app, ["analyze", str(src), "--backend", "mock"])
    assert result.exit_code == 0, result.output
    base = src / "specifications" / "product" / "specs" / "002-existing"
    assert (base / "spec.md").exists()
    assert (base / "review.md").exists()
    assert "main.py" in (base / "spec.md").read_text(encoding="utf-8")  # mock ехоїть код


def test_analyze_only_review(tmp_path):
    src = _src(tmp_path)
    result = runner.invoke(app, ["analyze", str(src), "--backend", "mock", "--only", "review"])
    assert result.exit_code == 0, result.output
    base = src / "specifications" / "product" / "specs" / "002-existing"
    assert (base / "review.md").exists()
    assert not (base / "spec.md").exists()


def test_analyze_slug_and_path(tmp_path):
    src = _src(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(
        app,
        ["analyze", str(src), "--path", str(out), "--slug", "custom", "--backend", "mock", "--only", "spec"],
    )
    assert result.exit_code == 0, result.output
    assert (out / "specifications" / "product" / "specs" / "custom" / "spec.md").exists()


def test_analyze_invalid_only(tmp_path):
    src = _src(tmp_path)
    result = runner.invoke(app, ["analyze", str(src), "--only", "bogus", "--backend", "mock"])
    assert result.exit_code != 0


def test_analyze_missing_source(tmp_path):
    result = runner.invoke(app, ["analyze", str(tmp_path / "nope"), "--backend", "mock"])
    assert result.exit_code == 1
