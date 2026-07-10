import logging

from spec_forge.export_pdf import EMOJI_FONT_PATH, export_bundle
from spec_forge.profiles import get_profile
from spec_forge.scaffolder import scaffold

import pytest


def _ctx() -> dict:
    return {"project": "demo", "summary": "s", **get_profile("python").render_context()}


def test_export_creates_timestamped_pdf(tmp_path):
    scaffold(tmp_path, _ctx())
    out = export_bundle(tmp_path)
    assert out.exists()
    assert out.parent.name == "exports"
    assert out.name.startswith("spec-forge-export-")
    assert out.suffix == ".pdf"
    assert out.read_bytes()[:4] == b"%PDF"


def test_emoji_font_is_bundled():
    assert EMOJI_FONT_PATH.exists(), "Noto Emoji fallback має їхати в пакеті"


def test_export_renders_emoji_via_fallback(tmp_path, caplog):
    """Файл з емодзі експортується: обидва шрифти вбудовано, без missing-glyph попереджень."""
    scaffold(tmp_path, _ctx())
    (tmp_path / "specifications" / "ICONS.md").write_text(
        "Статус: ✅ ❌ ⬜ 🟡 ⭐ 🤖 👤 🏛 🔌 🧩 🎨 🛠 💻 👥 🧠 📌", encoding="utf-8"
    )
    with caplog.at_level(logging.WARNING, logger="fpdf"):
        out = export_bundle(tmp_path)
    data = out.read_bytes()
    assert b"NotoEmoji" in data and b"DejaVuSans" in data  # обидва субсети вбудовано
    missing = [r for r in caplog.records if "not available" in r.getMessage().lower()]
    assert not missing, f"є символи без гліфа: {[r.getMessage() for r in missing]}"


def test_export_missing_bundle_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_bundle(tmp_path)
