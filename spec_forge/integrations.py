"""Інтеграція зі slash-командою Claude Code (`/spec-forge`).

Python-пакети не мають хуків на install/uninstall, тож:
- обгортка створюється **автоматично при першому запуску** CLI (ідемпотентно) — див. cli._main;
- прибирається командою `spec-forge command uninstall`;
- сама обгортка самозахисна: якщо `spec-forge` немає на PATH, вона нічого не виконує.
"""

from __future__ import annotations

from pathlib import Path

WRAPPER_NAME = "spec-forge.md"

_WRAPPER = """\
---
description: Запустити spec-forge CLI (генератор специфікацій) з аргументами
---
Користувач викликав `/spec-forge $ARGUMENTS`.

1. Перевір, що CLI доступний: `command -v spec-forge`. Якщо його немає — повідом, що
   spec-forge не встановлено (`uv tool install git+https://github.com/chiperi/spec-forge.git`),
   і зупинись, нічого не виконуючи.
2. Інакше виконай у терміналі: `spec-forge $ARGUMENTS`
3. Покажи вивід команди користувачу.
"""


def commands_dir(project_root: Path | None) -> Path:
    base = project_root if project_root is not None else Path.home()
    return base / ".claude" / "commands"


def command_path(project_root: Path | None = None) -> Path:
    return commands_dir(project_root) / WRAPPER_NAME


def ensure_installed(project_root: Path | None = None) -> tuple[Path, bool]:
    """Створює обгортку, якщо її немає. Повертає (шлях, чи_створено)."""
    path = command_path(project_root)
    if path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_WRAPPER, encoding="utf-8")
    return path, True


def remove(project_root: Path | None = None) -> tuple[Path, bool]:
    """Прибирає обгортку. Повертає (шлях, чи_прибрано)."""
    path = command_path(project_root)
    if path.exists():
        path.unlink()
        return path, True
    return path, False
