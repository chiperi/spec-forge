# ADR-0004: Інтеграція slash-команди /spec-forge (авто-provision)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer

## Context
Хотілося, щоб slash-команда Claude Code `/spec-forge` зʼявлялась і зникала «разом із аппкою».
Проблема: Python/uv-wheel **не має хуків** на install/uninstall — не можна зачепитися за
`uv tool install/uninstall`.

## Decision
- **Авто-додавання при першому запуску:** будь-яка команда CLI ідемпотентно створює
  `~/.claude/commands/spec-forge.md` (create-if-missing, не перезаписує).
- **Видалення:** `spec-forge command uninstall` (глобально або `--project`).
- **Самозахист обгортки:** вона спершу перевіряє `command -v spec-forge`; якщо тула немає —
  нічого не виконує (тож залишковий файл після `uv tool uninstall` нешкідливий).
- **Opt-out:** `SPEC_FORGE_NO_SLASH=1`.

## Consequences
**Позитивні**
- Практично «зʼявляється з аппкою» без ручного кроку; прибирається однією командою.
- Нема залежності від неіснуючих install-хуків.

**Негативні / компроміси**
- Справжнє авто-видалення на `uv tool uninstall` неможливе — лишається ручний `command uninstall`
  (файл при цьому інертний завдяки самозахисту).
- CLI пише у `~/.claude` (поза проєктом) — тому є явний opt-out.
