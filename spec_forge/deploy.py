"""Розгортання root-pointer-ів для tool-discovery (FR-008).

Створює symlinks у корені проєкту, що вказують у specifications/ (єдине джерело).
Лінкує лише те, що реально існує в bundle — тож працює і на мінімальному bundle.
"""

from __future__ import annotations

import os
from pathlib import Path

# (ім'я лінка в корені, ціль відносно кореня)
ROOT_LINKS: list[tuple[str, str]] = [
    ("AGENTS.md", "specifications/ai/AGENTS.md"),
    ("CLAUDE.md", "specifications/ai/AGENTS.md"),
    (".mcp.json", "specifications/ai/mcp/mcp.json"),
    (".editorconfig", "specifications/platform/editorconfig"),
    (".gitattributes", "specifications/platform/gitattributes"),
    (".tool-versions", "specifications/platform/tool-versions"),
    (".env.example", "specifications/platform/env.example"),
]

# (ім'я лінка, ціль відносно теки лінка)
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
        return  # не чіпаємо реальний файл/теку
    link.symlink_to(target)


def deploy_root(root: Path) -> list[str]:
    """Створює symlinks для наявних цілей. Повертає імена створених лінків."""
    created: list[str] = []
    for name, target in ROOT_LINKS:
        if (root / target).exists():
            _link(root / name, target)
            created.append(name)
    for name, target in NESTED_LINKS:
        link = root / name
        # ціль відносна до теки лінка; нормалізуємо текстово (тека лінка ще може не існувати)
        real = Path(os.path.normpath(link.parent / target))
        if real.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            _link(link, target)
            created.append(name)
    return created
