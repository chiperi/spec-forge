#!/usr/bin/env bash
# Remove the /spec-forge slash command + uninstall spec-forge.
# Usage:  ./uninstall.sh
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

echo "→ Removing the /spec-forge slash command ..."
spec-forge command uninstall || true   # while the CLI is still available; don't fail if already gone

echo "→ Uninstalling spec-forge ..."
uv tool uninstall spec-forge || true

echo "✅ Done: /spec-forge removed + spec-forge uninstalled."
