"""A bounded code-tree reader for brownfield analysis (the `analyze` command).

Following the export_pdf pattern: skips binary/large files and service directories, builds a tree + content
within a character budget. Deterministic, offline, dependency-free (a curated ignore-set instead of
parsing .gitignore — see ADR-0005).
"""

from __future__ import annotations

import os
from pathlib import Path

_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
    ".ruff_cache", ".pytest_cache", ".mypy_cache", ".tox", ".cache",
    "target", ".next", ".gradle", "coverage", ".idea",
    # the tool's own artifacts — don't ingest them back
    "specifications", "exports", ".spec-forge",
}
_SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".svg", ".webp",
    ".ttf", ".otf", ".woff", ".woff2", ".zip", ".gz", ".tar",
    ".so", ".dylib", ".dll", ".exe", ".o", ".a", ".class", ".jar",
    ".pyc", ".wasm", ".bin", ".map", ".mp4", ".mp3", ".mov",
}
_MAX_FILE_BYTES = 100_000
_MAX_TOTAL_CHARS = 200_000


def _is_text(path: Path) -> bool:
    if path.suffix.lower() in _SKIP_SUFFIXES:
        return False
    try:
        path.read_text(encoding="utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def _skip_file_name(name: str) -> bool:
    # secrets and junk
    return name == ".DS_Store" or name.startswith(".env")


def iter_source_files(root: Path, *, max_file_bytes: int = _MAX_FILE_BYTES) -> list[Path]:
    """Deterministic traversal: no service directories, symlinks, binaries, or oversized files."""
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        for name in sorted(filenames):
            if _skip_file_name(name):
                continue
            p = Path(dirpath) / name
            if p.is_symlink():
                continue
            try:
                if p.stat().st_size > max_file_bytes:
                    continue
            except OSError:
                continue
            if _is_text(p):
                found.append(p)
    return sorted(found, key=lambda p: p.as_posix())


def build_tree(root: Path, files: list[Path]) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for rel in sorted(f.relative_to(root).as_posix() for f in files):
        parts = rel.split("/")
        for i in range(len(parts) - 1):
            d = "/".join(parts[: i + 1])
            if d not in seen:
                seen.add(d)
                lines.append("  " * i + parts[i] + "/")
        lines.append("  " * (len(parts) - 1) + parts[-1])
    return "\n".join(lines)


def scan_codebase(
    root: Path,
    *,
    max_file_bytes: int = _MAX_FILE_BYTES,
    max_total_chars: int = _MAX_TOTAL_CHARS,
) -> str:
    """Tree + file content (bounded by max_total_chars). Returns a single context string."""
    files = iter_source_files(root, max_file_bytes=max_file_bytes)
    out = f"# File tree\n{build_tree(root, files)}\n\n# Files\n"
    used = len(out)
    omitted = 0
    chunks: list[str] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        block = f"\n--- {rel} ---\n{f.read_text(encoding='utf-8')}\n"
        if used + len(block) > max_total_chars:
            omitted += 1
            continue
        chunks.append(block)
        used += len(block)
    out += "".join(chunks)
    if omitted:
        out += f"\n… (truncated {omitted} files omitted)\n"
    return out
