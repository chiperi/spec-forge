from spec_forge.integrations import (
    WRAPPER_VERSION,
    bundled_agent_files,
    ensure_installed,
    remove,
)


def _cmd(root):
    return root / ".claude" / "commands" / "spec-forge.md"


def _agents(root):
    return root / ".claude" / "agents"


def test_install_writes_command_and_agents(tmp_path):
    result = ensure_installed(tmp_path)
    assert result.command_created
    assert _cmd(tmp_path).exists()
    srcs = bundled_agent_files()
    assert len(result.agents_created) == len(srcs) == 5
    for src in srcs:
        dst = _agents(tmp_path) / src.name
        assert dst.exists()
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8")


def test_agents_and_command_idempotent(tmp_path):
    ensure_installed(tmp_path)
    edited = _agents(tmp_path) / bundled_agent_files()[0].name
    edited.write_text("EDITED", encoding="utf-8")
    result = ensure_installed(tmp_path)
    assert result.command_created is False
    assert result.agents_created == []
    assert edited.read_text(encoding="utf-8") == "EDITED"  # ручна правка збережена


def test_command_self_upgrades_on_old_version(tmp_path):
    cmd = _cmd(tmp_path)
    cmd.parent.mkdir(parents=True, exist_ok=True)
    cmd.write_text("<!-- spec-forge-command v1 -->\nстара обгортка\n", encoding="utf-8")
    result = ensure_installed(tmp_path)
    assert result.command_created  # перезаписано на поточну версію
    assert f"spec-forge-command v{WRAPPER_VERSION}" in cmd.read_text(encoding="utf-8")


def test_wrapper_has_orchestrator_markers(tmp_path):
    ensure_installed(tmp_path)
    body = _cmd(tmp_path).read_text(encoding="utf-8")
    for marker in ("business-analyst", "solution-architect", "Task", "[NEEDS CLARIFICATION]", "v2"):
        assert marker in body
    assert "spec-forge $ARGUMENTS" not in body  # старого CLI-passthrough нема


def test_remove_removes_command_and_agents(tmp_path):
    ensure_installed(tmp_path)
    other = _agents(tmp_path) / "custom-other.md"
    other.write_text("keep me", encoding="utf-8")
    result = remove(tmp_path)
    assert result.command_removed
    assert len(result.agents_removed) == 5
    assert not _cmd(tmp_path).exists()
    assert other.exists()  # чужий агент не чіпаємо
    result2 = remove(tmp_path)
    assert not result2.command_removed
    assert result2.agents_removed == []


def test_bundled_agents_enumeration():
    names = {p.name for p in bundled_agent_files()}
    assert names == {
        "business-analyst.md",
        "solution-architect.md",
        "designer.md",
        "developer.md",
        "code-reviewer.md",
    }
