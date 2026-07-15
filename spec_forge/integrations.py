"""Інтеграція з Claude Code: slash-команда `/spec-forge` + рольові субагенти.

Python-пакети не мають хуків на install/uninstall, тож:
- команда + субагенти створюються автоматично при першому запуску CLI (ідемпотентно) — cli._main;
- прибираються командою `spec-forge command uninstall`;
- команда **self-upgrade** за версією (маркер `<!-- spec-forge-command vN -->` у файлі).

Runtime `/spec-forge` — це **диспетчер підкоманд**: `/spec-forge <підкоманда>` виконує точний
функціонал CLI. Контент (spec/plan/tasks/analyze/fill) генерується нативно в Claude Code (головний тред +
субагенти) на підписці Claude; механічні (init/validate/export/deploy/status) — локальним CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

WRAPPER_NAME = "spec-forge.md"
WRAPPER_VERSION = 6
AGENTS_SRC = Path(__file__).parent / "templates" / "bundle" / "ai" / "agents"

_WRAPPER = """\
---
description: Точні підкоманди spec-forge нативно в Claude Code (spec/plan/tasks/analyze/fill…), на підписці
argument-hint: <підкоманда> [аргументи] — spec | plan | tasks | analyze | fill | init | validate | export | deploy | status
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, TodoWrite, TaskCreate, TaskUpdate, TaskList
---
<!-- spec-forge-command v6 -->

Ти — **диспетчер** `/spec-forge <підкоманда> [аргументи]`. **Перший токен** `$ARGUMENTS` — це
підкоманда (той самий набір, що й у CLI `spec-forge`). Виконай ТОЧНО відповідний функціонал у теці
`specifications/` поточного проєкту. Не вгадуй «ціль своїми словами» — маршрутизуй за підкомандою.

Два класи підкоманд:
- **Контент** (`spec`, `plan`, `tasks`, `analyze`, `fill`) — генеруй **нативно тут**, у Claude Code, через
  рольових субагентів (`Task`). НЕ викликай CLI — контент генерується тут, на підписці Claude.
- **Механічні / детерміновані** (`init`, `validate`, `export`, `deploy`, `status`) — виконай локальний
  CLI: у терміналі `spec-forge $ARGUMENTS`, покажи вивід. Вони безкоштовні й детерміновані. Якщо
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

### `analyze [тека]` — brownfield: спека з коду + аудит дрейфу доків (in-place, код не чіпаємо)
Ціль — тека з `$ARGUMENTS` (типово `.`). Делегуй `Task` (subagent_type: `reverse-analyst`) — він сам
читає код цілі (пропускаючи `node_modules`, `.venv`, `.git`, бінарні/великі файли) →
`specifications/product/specs/002-existing/spec.md` (фактична спека, з посиланнями на файли). Тоді
`Task` (subagent_type: `reviewer`) — дай йому і наявні доки `specifications/`, і код: він **звіряє доки з
кодом**, знаходить чого бракує/недоліки й **дрейф** (код змінився, доки — ні) → `.../002-existing/review.md`
з **конкретними варіантами перезапису доків** (не застосовуй їх без підтвердження). **Гейт.**

### `fill` — покроковий майстер: заповнити ВСІ файли `specifications/` (native, з чеклистом прогресу)
Ціль — `specifications/` поточного проєкту (якщо бандла нема — спершу `init`). Режим **авто-чернетка → підтвердження**.

1. **Побудуй живий чеклист** (права todo-панель): `TodoWrite` (або `TaskCreate`/`TaskUpdate` — що доступно),
   по пункту на кожен **контентний** файл бандла, у порядку залежностей:
   `00-constitution.md` → `product/specs/**/spec.md` → `architecture/plan.md` → `architecture/decisions/*` →
   `contracts/*` → `architecture/nfr.md` → `delivery/tasks.md` → `design/*` → `roles/*` → `knowledge/*` → `README.md`.
   Суто **конфіг/детерміновані** файли (`.editorconfig`, `mcp.json`, `settings.json`, `tool-versions`,
   `gitattributes`, `editors/*`, `hooks/*`) познач як «scaffolded ✅ (skip)» — їх не заповнюємо інтерв'ю.
2. **Іди покроково.** На кожен файл (пункт → in-progress):
   - прочитай код проєкту (`Read`/`Grep`/`Glob`) і **накопичені відповіді з попередніх кроків**;
   - **сам зроби чернетку** (`Write`/`Edit`), узгоджену з кодом і вже заповненими файлами; де бракує входу — `[NEEDS CLARIFICATION]`;
   - покажи, що записав, і **зупинись на підтвердження** — користувач приймає/править (гейт);
   - онови пункт → ✅ і переходь до наступного.
3. Кожна відповідь користувача — **контекст для наступних кроків**: не питай двічі те, що вже відомо;
   пропонуй, спираючись на попереднє. Наприкінці запусти `spec-forge validate` (усі гейти зелені).

Важке (spec/plan/tasks) за потреби делегуй відповідному субагенту (`Task`), але **дай у бриф накопичений контекст**.

### `init` / `validate` / `export` / `deploy` / `status`
Виконай `spec-forge $ARGUMENTS` у терміналі й покажи вивід (детерміновано, локально).

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
