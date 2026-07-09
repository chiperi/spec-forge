from spec_forge.codescan import _is_text, iter_source_files, scan_codebase


def _make_tree(root):
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "x.js").write_text("x", encoding="utf-8")
    (root / ".venv").mkdir()
    (root / ".venv" / "y.py").write_text("y", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "z").write_text("z", encoding="utf-8")
    (root / "b.bin").write_bytes(b"\x00\x01\x02\xff")
    (root / "big.txt").write_text("x" * 5000, encoding="utf-8")


def test_iter_prunes_and_filters(tmp_path):
    _make_tree(tmp_path)
    files = iter_source_files(tmp_path, max_file_bytes=1000)
    names = {f.relative_to(tmp_path).as_posix() for f in files}
    assert "src/app.py" in names
    assert "README.md" in names
    assert not any("node_modules" in n for n in names)
    assert not any(".venv" in n for n in names)
    assert not any(".git" in n for n in names)
    assert "b.bin" not in names  # бінарний
    assert "big.txt" not in names  # завеликий
    assert files == sorted(files, key=lambda p: p.as_posix())  # детерміновано


def test_is_text_false_on_binary(tmp_path):
    binary = tmp_path / "x.bin"
    binary.write_bytes(b"\x00\xff")
    assert _is_text(binary) is False


def test_scan_contains_tree_and_bodies(tmp_path):
    _make_tree(tmp_path)
    out = scan_codebase(tmp_path, max_file_bytes=1000)
    assert "# File tree" in out
    assert "--- src/app.py ---" in out
    assert "def add" in out


def test_scan_truncates(tmp_path):
    for letter in "abc":
        (tmp_path / f"{letter}.md").write_text(letter.upper() * 400, encoding="utf-8")
    out = scan_codebase(tmp_path, max_total_chars=300)
    assert "truncated" in out
