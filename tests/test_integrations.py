from spec_forge.integrations import ensure_installed, remove


def test_install_and_remove_project(tmp_path):
    path, created = ensure_installed(tmp_path)
    assert created
    assert path.exists()
    assert path == tmp_path / ".claude" / "commands" / "spec-forge.md"
    assert "$ARGUMENTS" in path.read_text(encoding="utf-8")


def test_ensure_is_idempotent(tmp_path):
    ensure_installed(tmp_path)
    _, created_again = ensure_installed(tmp_path)
    assert not created_again


def test_remove(tmp_path):
    ensure_installed(tmp_path)
    path, removed = remove(tmp_path)
    assert removed
    assert not path.exists()
    _, removed_again = remove(tmp_path)
    assert not removed_again
