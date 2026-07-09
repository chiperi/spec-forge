#!/usr/bin/env bash
# Прибрати slash-команду /spec-forge + видалити spec-forge.
# Використання:  ./uninstall.sh
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

echo "→ Прибираю slash-команду /spec-forge ..."
spec-forge command uninstall || true   # поки CLI ще доступний; не падати, якщо вже нема

echo "→ Видаляю spec-forge ..."
uv tool uninstall spec-forge || true

echo "✅ Готово: /spec-forge прибрано + spec-forge видалено."
