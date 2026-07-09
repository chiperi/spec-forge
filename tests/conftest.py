import os

# Тести не мають торкатися реального ~/.claude — вимикаємо авто-встановлення slash-обгортки.
os.environ.setdefault("SPEC_FORGE_NO_SLASH", "1")
