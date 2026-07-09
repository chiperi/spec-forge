"""Інтеграція з Claude Code: slash-команда `/spec-forge` + рольові субагенти.

Python-пакети не мають хуків на install/uninstall, тож:
- команда + 5 субагентів створюються автоматично при першому запуску CLI (ідемпотентно) — cli._main;
- прибираються командою `spec-forge command uninstall`;
- команда **self-upgrade** за версією (маркер `<!-- spec-forge-command vN -->` у файлі).

Runtime `/spec-forge` — це діалоговий оркестратор: будує специфікацію нативно в Claude Code
(головний тред + субагенти), без CLI-викликів і без `ANTHROPIC_API_KEY` (працює на підписці).
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

WRAPPER_NAME = "spec-forge.md"
WRAPPER_VERSION = 2
AGENTS_SRC = Path(__file__).parent / "templates" / "bundle" / "ai" / "agents"

_WRAPPER = """\
---
description: Діалогом побудувати специфікацію (BA→SA→…) нативно в Claude Code, без API-ключа
argument-hint: [ціль / опис фічі]
allowed-tools: Task, Read, Write, Edit, Glob, Grep
---
<!-- spec-forge-command v2 -->

Ти — оркестратор spec-driven процесу. Будуй специфікацію **прямо тут, діалогом**, у теку
`specifications/` поточного проєкту. **Не** запускай CLI `spec-forge` для змісту і **не** потребуй
`ANTHROPIC_API_KEY` — увесь зміст генеруй нативно (ти + субагенти).

Ціль користувача: `$ARGUMENTS` (якщо порожньо — спитай, що специфікуємо).

Веди по фазах, з **людським гейтом** (підтвердженням) між кожною.

## 1. BA — вимоги → `specifications/product/specs/001-feature/spec.md`
Спершу **сам, у цьому діалозі**, проведи інтервʼю (субагенти не вміють питати користувача): запитай
домен, цілі / не-цілі, ключові user stories, обмеження, критерії успіху. Став уточнення, доки не
лишиться відкритих `[NEEDS CLARIFICATION]`.
Коли відповіді зібрано — делегуй чернетку через `Task` (subagent_type: `business-analyst`),
передавши **повний бриф** (усі відповіді + межі ролі) і шлях виводу. Формат: EARS / Given-When-Then,
незалежно тестовані user stories (P1 = MVP), вимірювані технологічно-незалежні success criteria,
glossary. Якщо `Task` недоступний — напиши spec.md сам за тими ж правилами. **Гейт.**

## 2. SA — план → `specifications/architecture/plan.md`
`Task` (subagent_type: `solution-architect`) з spec.md + брифом. Вивід: `architecture/plan.md`,
ADR у `specifications/architecture/decisions/`, контракти `specifications/contracts/openapi.yaml`
(за потреби asyncapi.yaml), NFR у числах. **Гейт.**

## 3. (Опційно) Designer — якщо є UI
Запропонуй; за згодою — `Task` (subagent_type: `designer`) → `specifications/design/<feature>.design.md`
(user flows, стани, a11y). **Гейт.**

## 4. (Опційно) Developer — задачі
Запропонуй; за згодою — `Task` (subagent_type: `developer`) → `specifications/delivery/tasks.md`
(атомарні, трасовані задачі). **Гейт.**

Правила: створюй потрібні теки/файли сам; при делегуванні давай **повний** самодостатній бриф
(субагент не бачить цей діалог); повторний запуск фази = оновлення, не дублювання; не змінюй код
проєкту без окремого прохання.
"""


class InstallResult(NamedTuple):
    command_path: Path
    command_created: bool
    agents_created: list[Path]


class RemoveResult(NamedTuple):
    command_path: Path
    command_removed: bool
    agents_removed: list[Path]


def commands_dir(project_root: Path | None) -> Path:
    base = project_root if project_root is not None else Path.home()
    return base / ".claude" / "commands"


def agents_dir(project_root: Path | None) -> Path:
    base = project_root if project_root is not None else Path.home()
    return base / ".claude" / "agents"


def command_path(project_root: Path | None = None) -> Path:
    return commands_dir(project_root) / WRAPPER_NAME


def bundled_agent_files() -> list[Path]:
    return sorted(AGENTS_SRC.glob("*.md"), key=lambda p: p.name)


def agent_paths(project_root: Path | None = None) -> list[Path]:
    target = agents_dir(project_root)
    return [target / src.name for src in bundled_agent_files()]


def _installed_version(text: str) -> int:
    marker = "spec-forge-command v"
    idx = text.find(marker)
    if idx == -1:
        return 0
    digits = ""
    for ch in text[idx + len(marker):]:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


def ensure_command_installed(project_root: Path | None = None, *, force: bool = False) -> tuple[Path, bool]:
    """Пише команду, якщо її нема / стара версія / force. Повертає (шлях, чи_записано)."""
    path = command_path(project_root)
    if not force and path.exists() and _installed_version(path.read_text(encoding="utf-8")) >= WRAPPER_VERSION:
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_WRAPPER, encoding="utf-8")
    return path, True


def ensure_agents_installed(project_root: Path | None = None, *, force: bool = False) -> list[Path]:
    """Копіює 5 субагентів (create-if-missing, або force). Повертає записані шляхи."""
    created: list[Path] = []
    target = agents_dir(project_root)
    for src in bundled_agent_files():
        dst = target / src.name
        if force or not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            created.append(dst)
    return created


def ensure_installed(project_root: Path | None = None, *, force: bool = False) -> InstallResult:
    cmd_path, cmd_created = ensure_command_installed(project_root, force=force)
    agents_created = ensure_agents_installed(project_root, force=force)
    return InstallResult(cmd_path, cmd_created, agents_created)


def remove(project_root: Path | None = None) -> RemoveResult:
    cmd_path = command_path(project_root)
    cmd_removed = False
    if cmd_path.exists():
        cmd_path.unlink()
        cmd_removed = True
    removed_agents: list[Path] = []
    for dst in agent_paths(project_root):
        if dst.exists():
            dst.unlink()
            removed_agents.append(dst)
    return RemoveResult(cmd_path, cmd_removed, removed_agents)
