"""Експорт усіх файлів bundle у єдиний PDF-знімок (FR-013).

Навіщо: команда відкриває один документ, вичитує всю специфікацію й позначає, у яких
файлах треба зміни. Імʼя містить таймстемп; PDF складається в окрему теку `exports/`.
Кирилиця — через вбудований DejaVuSans (базові PDF-шрифти її не підтримують). Іконки-емодзі
(✅ ❌ ⬜ 🟡 ⭐ 🤖 …), яких немає в DejaVuSans, домальовуються з вбудованого Noto Emoji
(monochrome) через per-glyph fallback fpdf2 — текст лишається DejaVu, іконки беруться з Noto.
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
_MAX_CHARS = 60_000  # захист від величезного файлу в одному PDF


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
    """Генерує PDF усіх текстових файлів specifications/. Повертає шлях до PDF."""
    bundle = project / "specifications"
    if not bundle.exists():
        raise FileNotFoundError(f"{bundle} не існує — спершу `spec-forge init`")

    files = _text_files(bundle)
    ts = _timestamp()

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", str(FONT_PATH))
    # Fallback для іконок-емодзі, яких немає в DejaVuSans (fpdf2 підставляє гліфи по-символьно).
    if EMOJI_FONT_PATH.exists():
        pdf.add_font("NotoEmoji", "", str(EMOJI_FONT_PATH))
        pdf.set_fallback_fonts(["NotoEmoji"])

    def cell(height: float, text: str) -> None:
        # new_x/new_y повертають курсор на лівий берег наступного рядка (fpdf2)
        pdf.multi_cell(0, height, text, wrapmode="CHAR", new_x="LMARGIN", new_y="NEXT")

    # титул + зміст
    pdf.add_page()
    pdf.set_font("DejaVu", size=18)
    cell(10, "spec-forge — знімок специфікації")
    pdf.set_font("DejaVu", size=10)
    cell(6, f"Проєкт: {project.name}\nЗгенеровано: {ts}\nФайлів: {len(files)}")
    pdf.ln(3)
    pdf.set_font("DejaVu", size=12)
    cell(7, "Зміст (перелік файлів для рев'ю):")
    pdf.set_font("DejaVu", size=9)
    for i, path in enumerate(files, 1):
        cell(5, f"{i:>3}. specifications/{path.relative_to(bundle).as_posix()}")

    # по файлу — окрема сторінка
    for i, path in enumerate(files, 1):
        pdf.add_page()
        rel = path.relative_to(bundle).as_posix()
        pdf.set_font("DejaVu", size=13)
        cell(8, f"[{i}] specifications/{rel}")
        pdf.ln(1)
        pdf.set_font("DejaVu", size=8)
        content = path.read_text(encoding="utf-8")
        if len(content) > _MAX_CHARS:
            content = content[:_MAX_CHARS] + "\n… (обрізано)"
        cell(4, content)

    out_dir = project / out_dirname
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"spec-forge-export-{ts}.pdf"
    pdf.output(str(out))
    return out
