"""Deploying root pointers for tool-discovery (FR-008).

Creates symlinks in the project root that point into specifications/ (the single source).
Links only what actually exists in the bundle — so it works even on a minimal bundle.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

# (link name in the root, target relative to the root)
ROOT_LINKS: list[tuple[str, str]] = [
    ("AGENTS.md", "specifications/ai/AGENTS.md"),
    ("CLAUDE.md", "specifications/ai/AGENTS.md"),
    (".mcp.json", "specifications/ai/mcp/mcp.json"),
    (".editorconfig", "specifications/platform/editorconfig"),
    (".tool-versions", "specifications/platform/tool-versions"),
    (".env.example", "specifications/platform/env.example"),
]

# git reads these files with O_NOFOLLOW (protection against symlink attacks) and does NOT follow the symlink,
# so in the root they MUST be real files — otherwise the rules are ignored
# ("Too many levels of symbolic links"). That's why we copy the content rather than link it.
ROOT_COPIES: list[tuple[str, str]] = [
    (".gitattributes", "specifications/platform/gitattributes"),
]

# (link name, target relative to the link's directory)
NESTED_LINKS: list[tuple[str, str]] = [
    (".claude/agents", "../specifications/ai/agents"),
    (".claude/commands", "../specifications/ai/commands"),
    (".claude/skills", "../specifications/ai/skills"),
    (".claude/hooks", "../specifications/ai/hooks"),
    (".claude/settings.json", "../specifications/ai/settings.json"),
    (".github/copilot-instructions.md", "../specifications/ai/rules/copilot-instructions.md"),
    (".github/workflows", "../specifications/quality/workflows"),
]


def _link(link: Path, target: str) -> None:
    if link.is_symlink():
        link.unlink()
    elif link.exists():
        return  # don't touch a real file/directory
    link.symlink_to(target)


def _copy(dst: Path, src: Path) -> None:
    """Materializes a real file (for git-sensitive targets). Updates when the source changes."""
    if dst.is_symlink():
        dst.unlink()
    new = src.read_bytes()
    if dst.exists() and dst.read_bytes() == new:
        return
    shutil.copyfile(src, dst)


def deploy_root(root: Path) -> list[str]:
    """Creates root pointers for existing targets. Returns the names of the created ones.

    Mostly symlinks; git-sensitive files (`ROOT_COPIES`) are real copies.
    """
    created: list[str] = []
    for name, target in ROOT_LINKS:
        if (root / target).exists():
            _link(root / name, target)
            created.append(name)
    for name, target in ROOT_COPIES:
        src = root / target
        if src.exists():
            _copy(root / name, src)
            created.append(name)
    for name, target in NESTED_LINKS:
        link = root / name
        # target is relative to the link's directory; normalize textually (the link's directory may not exist yet)
        real = Path(os.path.normpath(link.parent / target))
        if real.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            _link(link, target)
            created.append(name)
    return created
