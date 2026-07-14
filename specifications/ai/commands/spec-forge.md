---
description: Точні підкоманди spec-forge нативно в Claude Code (spec/plan/tasks/analyze…), на підписці
argument-hint: <підкоманда> [аргументи] — spec | plan | tasks | analyze | init | validate | export | deploy | status
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash
---
<!-- spec-forge-command v5 -->

Ти — **диспетчер** `/spec-forge <підкоманда> [аргументи]`. **Перший токен** `$ARGUMENTS` — це
підкоманда (той самий набір, що й у CLI `spec-forge`). Виконай ТОЧНО відповідний функціонал у теці
`specifications/` поточного проєкту. Не вгадуй «ціль своїми словами» — маршрутизуй за підкомандою.

Два класи підкоманд:
- **Контент** (`spec`, `plan`, `tasks`, `analyze`) — генеруй **нативно тут**, у Claude Code, через
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

### `init` / `validate` / `export` / `deploy` / `status`
Виконай `spec-forge $ARGUMENTS` у терміналі й покажи вивід (детерміновано, локально).

### порожньо або `help`
Покажи список підкоманд вище (по рядку-опису на кожну) і зупинись.

Правила: делегуючи, давай самодостатній бриф (субагент не бачить цей діалог); людський гейт після
кожної контентної фази; повторний запуск = оновлення, не дубль; код проєкту без окремого прохання не змінюй.
