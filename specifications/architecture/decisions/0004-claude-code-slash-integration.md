# ADR-0004: Integration of the /spec-forge slash command (auto-provision)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer

## Context
We wanted the Claude Code slash command `/spec-forge` to appear and disappear "together with the app".
The problem: a Python/uv wheel **has no hooks** on install/uninstall — you cannot hook into
`uv tool install/uninstall`.

## Decision
- **Auto-add on first run:** any CLI command idempotently creates
  `~/.claude/commands/spec-forge.md` (create-if-missing, does not overwrite).
- **Removal:** `spec-forge command uninstall` (globally or `--project`).
- **Wrapper self-protection:** it first checks `command -v spec-forge`; if the tool is absent —
  it does nothing (so a leftover file after `uv tool uninstall` is harmless).
- **Opt-out:** `SPEC_FORGE_NO_SLASH=1`.
- **Binding with `uv tool` (Approach 1):** `install.sh` / `uninstall.sh` (+ `just install|uninstall`)
  install/remove the CLI and the slash wrapper **together** — because wheel hooks on install/uninstall do not exist.

## Consequences
**Positive**
- Practically "appears with the app" without a manual step; removed with a single command.
- No dependency on non-existent install hooks.

**Negative / trade-offs**
- Real auto-removal on `uv tool uninstall` is impossible — a manual `command uninstall` remains
  (the file being inert in the meantime thanks to self-protection).
- The CLI writes to `~/.claude` (outside the project) — hence the explicit opt-out.
