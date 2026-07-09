"""Інтеграція з Claude Code: slash-команда `/spec-forge` + рольові субагенти.

Python-пакети не мають хуків на install/uninstall, тож:
- команда + субагенти створюються автоматично при першому запуску CLI (ідемпотентно) — cli._main;
- прибираються командою `spec-forge command uninstall`;
- команда **self-upgrade** за версією (маркер `<!-- spec-forge-command vN -->` у файлі).

Runtime `/spec-forge` — це **диспетчер підкоманд**: `/spec-forge <підкоманда>` виконує точний
функціонал CLI. Контент (spec/plan/tasks/analyze) генерується нативно в Claude Code (головний тред +
субагенти), без API-ключа (на підписці); механічні (init/validate/export/deploy/status) — локальним CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

WRAPPER_NAME = "spec-forge.md"
WRAPPER_VERSION = 3
AGENTS_SRC = Path(__file__).parent / "templates" / "bundle" / "ai" / "agents"

_WRAPPER = """\
---
description: Точні підкоманди spec-forge нативно в Claude Code (spec/plan/tasks/analyze…), без API-ключа
argument-hint: <підкоманда> [аргументи] — spec | plan | tasks | analyze | init | validate | export | deploy | status
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash
---
<!-- spec-forge-command v3 -->

Ти — **диспетчер** `/spec-forge <підкоманда> [аргументи]`. **Перший токен** `$ARGUMENTS` — це
підкоманда (той самий набір, що й у CLI `spec-forge`). Виконай ТОЧНО відповідний функціонал у теці
`specifications/` поточного проєкту. Не вгадуй «ціль своїми словами» — маршрутизуй за підкомандою.

Два класи підкоманд:
- **Контент** (`spec`, `plan`, `tasks`, `analyze`) — генеруй **нативно тут**, у Claude Code, через
  рольових субагентів (`Task`). НЕ викликай CLI і **не** потребуй `ANTHROPIC_API_KEY` (працює на підписці).
- **Механічні / детерміновані** (`init`, `validate`, `export`, `deploy`, `status`) — виконай локальний
  CLI: у терміналі `spec-forge $ARGUMENTS`, покажи вивід. Вони безкоштовні й не чіпають API. Якщо
  `spec-forge` не знайдено (`command -v spec-forge`) — скажи, як поставити, і зупинись.

## Маршрутизація

### `spec [опис]` — BA → `specifications/product/specs/001-feature/spec.md`
Якщо вхідних бракує — коротко доуточни у діалозі (субагент не вміє питати користувача) і закрий
`[NEEDS CLARIFICATION]`. Тоді делегуй `Task` (subagent_type: `business-analyst`) з **повним брифом**
→ spec.md: EARS / Given-When-Then, тестовані user stories (P1 = MVP), вимірювані success criteria,
glossary. **Гейт.**

### `plan` — SA → `specifications/architecture/plan.md`
Прочитай spec.md. `Task` (subagent_type: `solution-architect`) → `architecture/plan.md` + ADR у
`architecture/decisions/` + контракти `contracts/openapi.yaml` (за потреби asyncapi.yaml), NFR у числах. **Гейт.**

### `tasks` — Developer → `specifications/delivery/tasks.md`
Прочитай plan.md. `Task` (subagent_type: `developer`) → атомарні трасовані задачі. **Гейт.**

### `analyze [тека]` — brownfield (in-place, код не чіпаємо)
Ціль — тека з `$ARGUMENTS` (типово `.`). Делегуй `Task` (subagent_type: `reverse-analyst`) — він сам
читає код цілі (пропускаючи `node_modules`, `.venv`, `.git`, бінарні/великі файли) →
`specifications/product/specs/002-existing/spec.md` (фактична спека, з посиланнями на файли). Тоді
`Task` (subagent_type: `reviewer`) → `.../002-existing/review.md` (gap / де і що виправити). **Гейт.**

### `init` / `validate` / `export` / `deploy` / `status`
Виконай `spec-forge $ARGUMENTS` у терміналі й покажи вивід (детерміновано, без API).

### порожньо або `help`
Покажи список підкоманд вище (по рядку-опису на кожну) і зупинись.

Правила: делегуючи, давай самодостатній бриф (субагент не бачить цей діалог); людський гейт після
кожної контентної фази; повторний запуск = оновлення, не дубль; код проєкту без окремого прохання не змінюй.
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
    """Копіює бандл-субагентів (create-if-missing, або force). Повертає записані шляхи."""
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
