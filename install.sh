#!/usr/bin/env bash
# Install spec-forge globally + register the Claude Code /spec-forge slash command.
# Usage:  ./install.sh
#   curl -fsSL https://raw.githubusercontent.com/chiperi/spec-forge/main/install.sh | bash
set -euo pipefail

REPO="${SPEC_FORGE_REPO:-git+https://github.com/chiperi/spec-forge.git}"

echo "→ Installing spec-forge ($REPO) ..."
uv tool install --force "$REPO"

# make sure the executable is visible in this run
export PATH="$HOME/.local/bin:$PATH"

echo "→ Registering the /spec-forge slash command ..."
spec-forge command install

echo "✅ Done: spec-forge installed + /spec-forge registered."
echo "   If the command isn't found in a new terminal — run: uv tool update-shell"
echo "   Reload Claude Code to see /spec-forge in the menu."
