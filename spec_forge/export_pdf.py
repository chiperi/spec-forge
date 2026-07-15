"""Export all bundle files into a single PDF snapshot (FR-013).

Why: the team opens one document, reads the entire specification, and marks which
files need changes. The name contains a timestamp; the PDF is placed in a separate `exports/` directory.
Cyrillic is handled via the embedded DejaVuSans (the base PDF fonts don't support it). Emoji icons
(✅ ❌ ⬜ 🟡 ⭐ 🤖 …) that are missing from DejaVuSans are drawn from the embedded Noto Emoji
(monochrome) via fpdf2's per-glyph fallback — text stays DejaVu, icons come from Noto.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from fpdf import FPDF

_FONTS = Path(__file__).parent / "assets" / "fonts"
FONT_PATH = _FONTS / "DejaVuSans.ttf"
EMOJI_FONT_PATH = _FONTS / "NotoEmoji.ttf"

_SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf",
    ".ttf", ".otf", ".woff", ".woff2", ".zip", ".gz",
}
_MAX_CHARS = 60_000  # guard against a huge file in a single PDF


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _is_text(path: Path) -> bool:
    if path.suffix.lower() in _SKIP_SUFFIXES:
        return False
    try:
        path.read_text(encoding="utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def _text_files(bundle: Path) -> list[Path]:
    files = [
        p
        for p in bundle.rglob("*")
        if p.is_file() and not p.is_symlink() and _is_text(p)
    ]
    return sorted(files, key=lambda p: p.as_posix())


def export_bundle(project: Path, out_dirname: str = "exports") -> Path:
    """Generates a PDF of all text files in specifications/. Returns the path to the PDF."""
    bundle = project / "specifications"
    if not bundle.exists():
        raise FileNotFoundError(f"{bundle} does not exist — run `spec-forge init` first")

    files = _text_files(bundle)
    ts = _timestamp()

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", str(FONT_PATH))
    # Fallback for emoji icons missing from DejaVuSans (fpdf2 substitutes glyphs per-character).
    if EMOJI_FONT_PATH.exists():
        pdf.add_font("NotoEmoji", "", str(EMOJI_FONT_PATH))
        pdf.set_fallback_fonts(["NotoEmoji"])

    def cell(height: float, text: str) -> None:
        # new_x/new_y return the cursor to the left margin of the next line (fpdf2)
        pdf.multi_cell(0, height, text, wrapmode="CHAR", new_x="LMARGIN", new_y="NEXT")

    # title + contents
    pdf.add_page()
    pdf.set_font("DejaVu", size=18)
    cell(10, "spec-forge — specification snapshot")
    pdf.set_font("DejaVu", size=10)
    cell(6, f"Project: {project.name}\nGenerated: {ts}\nFiles: {len(files)}")
    pdf.ln(3)
    pdf.set_font("DejaVu", size=12)
    cell(7, "Contents (list of files for review):")
    pdf.set_font("DejaVu", size=9)
    for i, path in enumerate(files, 1):
        cell(5, f"{i:>3}. specifications/{path.relative_to(bundle).as_posix()}")

    # one page per file
    for i, path in enumerate(files, 1):
        pdf.add_page()
        rel = path.relative_to(bundle).as_posix()
        pdf.set_font("DejaVu", size=13)
        cell(8, f"[{i}] specifications/{rel}")
        pdf.ln(1)
        pdf.set_font("DejaVu", size=8)
        content = path.read_text(encoding="utf-8")
        if len(content) > _MAX_CHARS:
            content = content[:_MAX_CHARS] + "\n… (truncated)"
        cell(4, content)

    out_dir = project / out_dirname
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"spec-forge-export-{ts}.pdf"
    pdf.output(str(out))
    return out
