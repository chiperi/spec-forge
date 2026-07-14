# ADR-0005: `analyze` — reverse-спека + рев'ю наявного коду

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer (+ SA)

## Context
Greenfield-режим драфтить з опису (`-d`) + `AGENTS.md`, **не читаючи код**. Потрібен brownfield:
за наявним кодом отримати (1) reverse-спеку (що робить) і (2) рев'ю (де/що виправити, чи все як треба).

## Decision
- Одна команда **`analyze <source>`**: один скан коду → два документи (`--only both|spec|review`).
- **In-place:** пише у `<source>/specifications/product/specs/002-existing/{spec,review}.md`
  (`--path` / `--slug` — override). **Код не чіпає.**
- **`init` не потрібен** (brownfield): теки створює `_write_artifact`.
- Читач коду **`codescan.py`** — курований ignore-set (без `.gitignore`/`pathspec`): детермінований,
  офлайн, тестований; ліміти `--max-file-bytes` / `--max-chars`.
- Дві нові персони: **`reverse-analyst`**, **`reviewer`**.
- Фази `analyze` / `review` — через `mark_phase`/`phase_done` (re-spec diff/confirm), але **НЕ** у `state.PHASES`
  (щоб не міняти `status`/`validate`).

## Consequences
**Позитивні**
- Reuse `_run_phase` / `_write_artifact` / `_read_first_spec`; жодної нової залежності.
- Reverse-спека — first-class: її бачать `validate` / `export` / `plan`.

**Негативні / компроміси**
- Реальний зміст — нативно через `/spec-forge analyze` (Claude Code); CLI `analyze` — ехо
  (тести/офлайн-каркас).
- `.gitignore` не парситься — відкладено (майбутній `--gitignore` + `pathspec`).
- Великі репо обрізаються `--max-chars` (обмеження контексту субагента).
