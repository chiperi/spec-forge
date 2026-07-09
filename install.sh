#!/usr/bin/env bash
# Встановити spec-forge глобально + зареєструвати slash-команду Claude Code /spec-forge.
# Використання:  ./install.sh
#   curl -fsSL https://raw.githubusercontent.com/chiperi/spec-forge/main/install.sh | bash
set -euo pipefail

REPO="${SPEC_FORGE_REPO:-git+https://github.com/chiperi/spec-forge.git}"

echo "→ Встановлюю spec-forge ($REPO) ..."
uv tool install --force "$REPO"

# гарантуємо, що виконуваний файл видно в цьому запуску
export PATH="$HOME/.local/bin:$PATH"

echo "→ Реєструю slash-команду /spec-forge ..."
spec-forge command install

echo "✅ Готово: spec-forge встановлено + /spec-forge зареєстровано."
echo "   Якщо команда не знайдена у новому терміналі — виконай: uv tool update-shell"
echo "   Перезавантаж Claude Code, щоб побачити /spec-forge у меню."
