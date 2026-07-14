"""Розгортання root-pointer-ів для tool-discovery (FR-008).

Створює symlinks у корені проєкту, що вказують у specifications/ (єдине джерело).
Лінкує лише те, що реально існує в bundle — тож працює і на мінімальному bundle.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

# (ім'я лінка в корені, ціль відносно кореня)
ROOT_LINKS: list[tuple[str, str]] = [
    ("AGENTS.md", "specifications/ai/AGENTS.md"),
    ("CLAUDE.md", "specifications/ai/AGENTS.md"),
    (".mcp.json", "specifications/ai/mcp/mcp.json"),
    (".editorconfig", "specifications/platform/editorconfig"),
    (".tool-versions", "specifications/platform/tool-versions"),
    (".env.example", "specifications/platform/env.example"),
]

# git читає ці файли з O_NOFOLLOW (захист від symlink-атак) і НЕ йде за симлінком,
# тож у корені вони МАЮТЬ бути реальними файлами — інакше правила ігноруються
# ("Too many levels of symbolic links"). Тому копіюємо вміст, а не лінкуємо.
ROOT_COPIES: list[tuple[str, str]] = [
    (".gitattributes", "specifications/platform/gitattributes"),
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


def _copy(dst: Path, src: Path) -> None:
    """Матеріалізує реальний файл (для git-чутливих цілей). Оновлює за зміни джерела."""
    if dst.is_symlink():
        dst.unlink()
    new = src.read_bytes()
    if dst.exists() and dst.read_bytes() == new:
        return
    shutil.copyfile(src, dst)


def deploy_root(root: Path) -> list[str]:
    """Створює root-pointer-и для наявних цілей. Повертає імена створених.

    Здебільшого symlinks; git-чутливі файли (`ROOT_COPIES`) — реальні копії.
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
        # ціль відносна до теки лінка; нормалізуємо текстово (тека лінка ще може не існувати)
        real = Path(os.path.normpath(link.parent / target))
        if real.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            _link(link, target)
            created.append(name)
    return created
