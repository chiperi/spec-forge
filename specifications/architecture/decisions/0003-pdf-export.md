# ADR-0003: PDF export via fpdf2 + DejaVuSans (+ Noto Emoji fallback)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer (+ SA)

## Context
We need an `export` — to assemble all `specifications/` files into a single PDF (a timestamped name, a separate
`exports/` directory) for team review. The content is mostly Cyrillic; the base PDF fonts do not have it.
Candidates: fpdf2 (pure-python, pip), reportlab (heavier), weasyprint (system dependencies pango/cairo).

## Decision
- Generation via **fpdf2** (pure-python, no system dependencies, cross-platform).
- Cyrillic — an **embedded `DejaVuSans.ttf`** in `spec_forge/assets/fonts/` (free license).
- Emoji icons (✅ ❌ ⬜ 🟡 ⭐ 🤖 …) that DejaVuSans lacks — via a **fallback font
  `NotoEmoji.ttf`** (Noto Emoji monochrome, OFL) and `pdf.set_fallback_fonts([...])`: fpdf2 substitutes
  the missing glyphs per-character, keeping the text in DejaVu. fpdf2 does not embed color emoji → monochrome.
- `multi_cell(..., wrapmode="CHAR", new_x="LMARGIN", new_y="NEXT")` — so that long lines of code do not
  overflow the margin and the cursor moves to a new line correctly.
- Output: `<project>/exports/spec-forge-export-YYYY-MM-DD_HH-MM-SS.pdf`.

## Consequences
**Positive**
- Cross-platform (works in CI on 3 OSes), without system libraries.
- One self-contained document for review; a separate `exports/` directory (in `.gitignore`).

**Negative / trade-offs**
- The embedded fonts add ~756 KB (DejaVuSans) + ~866 KB (NotoEmoji, static instance) to the repo.
- Emoji are rendered **monochrome** (fpdf2 does not embed color COLR/bitmap fonts) — acceptable for a spec PDF.

## Alternatives considered
- **reportlab** — more powerful, but heavier and also requires registering a Unicode font.
- **weasyprint** — good HTML→PDF, but pulls in system dependencies (pango/cairo) — fragile in CI.
