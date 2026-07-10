# ADR-0003: PDF-експорт через fpdf2 + DejaVuSans (+ Noto Emoji fallback)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer (+ SA)

## Context
Потрібен `export` — зібрати всі файли `specifications/` в один PDF (імʼя з таймстемпом, окрема
тека `exports/`) для командного рев'ю. Контент — переважно кирилиця; базові PDF-шрифти її не мають.
Кандидати: fpdf2 (pure-python, pip), reportlab (важче), weasyprint (системні залежності pango/cairo).

## Decision
- Генерація через **fpdf2** (pure-python, без системних залежностей, крос-платформно).
- Кирилиця — **вбудований `DejaVuSans.ttf`** у `spec_forge/assets/fonts/` (вільна ліцензія).
- Іконки-емодзі (✅ ❌ ⬜ 🟡 ⭐ 🤖 …), яких немає в DejaVuSans, — через **fallback-шрифт
  `NotoEmoji.ttf`** (Noto Emoji monochrome, OFL) і `pdf.set_fallback_fonts([...])`: fpdf2 підставляє
  відсутні гліфи по-символьно, лишаючи текст у DejaVu. Кольорові емодзі fpdf2 не вбудовує → монохром.
- `multi_cell(..., wrapmode="CHAR", new_x="LMARGIN", new_y="NEXT")` — щоб довгі рядки коду не
  «вилазили» за поле й курсор коректно переходив на новий рядок.
- Вихід: `<project>/exports/spec-forge-export-YYYY-MM-DD_HH-MM-SS.pdf`.

## Consequences
**Позитивні**
- Крос-платформно (працює в CI на 3 ОС), без системних бібліотек.
- Один самодостатній документ для рев'ю; окрема тека `exports/` (у `.gitignore`).

**Негативні / компроміси**
- Вбудовані шрифти додають ~756 КБ (DejaVuSans) + ~866 КБ (NotoEmoji, статичний інстанс) у репо.
- Емодзі рендеряться **монохромно** (fpdf2 не вбудовує кольорові COLR/bitmap-шрифти) — прийнятно для спек-PDF.

## Alternatives considered
- **reportlab** — потужніший, але важчий і теж потребує реєстрації Unicode-шрифту.
- **weasyprint** — гарний HTML→PDF, але тягне системні залежності (pango/cairo) — крихко в CI.
