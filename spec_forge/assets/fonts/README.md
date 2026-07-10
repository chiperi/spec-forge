# Bundled fonts

`DejaVuSans.ttf` — DejaVu Fonts (Bitstream Vera / Arev derivative). Вільна ліцензія,
дозволяє редистрибуцію. Основний шрифт PDF-експорту: містить кирилицю (базові шрифти PDF
її не підтримують). Джерело: проєкт DejaVu Fonts (https://dejavu-fonts.github.io/).

`NotoEmoji.ttf` — Noto Emoji (monochrome), статичний інстанс `wght=400`. Ліцензія
**SIL Open Font License 1.1** (див. `NotoEmoji-OFL.txt`), дозволяє вбудовування й редистрибуцію.
**Fallback**-шрифт: fpdf2 бере з нього гліфи іконок-емодзі (✅ ❌ ⬜ 🟡 ⭐ 🤖 …), яких немає в
DejaVuSans. Джерело: Google Noto Emoji (https://github.com/googlefonts/noto-emoji), OFL з
google/fonts. Кольорові емодзі fpdf2 не вбудовує — іконки монохромні.
