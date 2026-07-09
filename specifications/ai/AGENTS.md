# AGENTS.md — spec-forge

> ⭐ ЄДИНЕ джерело правди для всіх AI-агентів. `CLAUDE.md`/`GEMINI.md` → symlink на цей файл.

## Project overview
**spec-forge** — CLI-інструмент, що генерує якісну, портовану, AI/OS-friendly специфікацію
(`specifications/` бандл) для **будь-якого** проєкту й стеку. Гібрид: детермінований двигун
(скафолдинг + lifecycle + валідація) + AI-субагенти (BA/SA/Designer/Developer) для наповнення змістом.
Повна спека продукту — у `../product/specs/001-spec-generation/spec.md`.

## Tech stack
- Мова / рантайм: **Python 3.12+** (type hints)
- CLI: **Typer**
- Пакет-менеджер: **uv**
- Тести: **pytest** (+ coverage)
- Лінт/формат: **Ruff**
- AI-бекенд: **Anthropic Messages API** (пакет `anthropic`), модель `claude-opus-4-8` (ADR-0002)
- Вихід тула (spec bundle) — **stack-agnostic**: цільовий стек задається stack-profile, не хардкодиться.

## Setup commands
```bash
uv sync            # встановити залежності
uv run spec-forge  # запустити CLI
uv run pytest      # тести
uv run ruff check  # лінт
uv run ruff format # формат
```
> Значення baseline; уточнюються на SA-фазі (`plan.md`).

## Code style
- Ruff (lint + format); type hints обовʼязкові; без `any`-подібних лазівок.
- Ядро двигуна — детерміноване й тестоване; жодного хардкоду конкретного стеку в ядрі.

## Testing
- Unit — двигун (скафолдинг, рендер, валідатори); поріг coverage уточнюється в NFR.
- Детермінізм: однакові входи → ідентичний вихід (перевіряти в CI, matrix по ОС).

## Workflow
Спершу спека (`product/specs/`), потім архітектура (`architecture/plan.md` + `decisions/`), потім код.
Фази з людським gate між ними. Важливі рішення → ADR у `../architecture/decisions/`.

## Security & guardrails
- Не комітати секрети / `.env`.
- Не змінювати структуру бандла мовчки — це артефакт шаблону.
- Без масштабних рефакторингів «заодно» — тільки поставлена задача.
