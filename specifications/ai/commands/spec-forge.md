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
