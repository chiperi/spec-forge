# spec-forge

Stack-agnostic, spec-driven development CLI: turn any project into a complete,
**AI- & OS-friendly specification bundle**. Deterministic scaffolding + Claude-powered
drafting across BA / SA / Developer personas, quality gates, lifecycle state, and
one-command tool-discovery deploy.

## Install (CLI + Claude Code command together)

Installs the global CLI **and** registers the `/spec-forge` Claude Code command in one step:

```bash
curl -fsSL https://raw.githubusercontent.com/chiperi/spec-forge/main/install.sh | bash
# or from a clone:   just install     (same as ./install.sh)
```

Remove **both** together:

```bash
./uninstall.sh          # or:  just uninstall
```

- Upgrade: re-run the installer (or `uv tool upgrade spec-forge`).
- If `spec-forge` isn't found, put `~/.local/bin` on `PATH` (`uv tool update-shell`).

<details><summary>Raw uv (CLI only)</summary>

```bash
uv tool install git+https://github.com/chiperi/spec-forge.git
```

The `/spec-forge` wrapper is then auto-registered on first run — see *Claude Code integration* below.
</details>

## Claude Code integration (`/spec-forge`)

On first run, spec-forge auto-registers a Claude Code slash command at
`~/.claude/commands/spec-forge.md`, so you can call `/spec-forge <args>` in chat.

- Add/remove explicitly: `spec-forge command install [--project]` · `spec-forge command uninstall`.
- Opt out of auto-registration: `export SPEC_FORGE_NO_SLASH=1`.
- The wrapper self-guards: if `spec-forge` isn't on `PATH` it does nothing (safe to leave behind).

> Note: Python/uv has no uninstall hooks, so `uv tool uninstall` can't auto-remove the wrapper —
> run `spec-forge command uninstall` (or delete the file). Reload Claude Code to see the command.

## Develop (from source)

```bash
git clone https://github.com/chiperi/spec-forge.git
cd spec-forge
uv sync
uv run spec-forge --help
```

## Usage

```bash
uv run spec-forge init <dir> --name "My App" --stack python   # scaffold specifications/
uv run spec-forge spec  <dir> -d "what to build" --backend claude   # BA → spec.md
uv run spec-forge plan  <dir> --backend claude                # SA → plan.md
uv run spec-forge tasks <dir> --backend claude                # → delivery/tasks.md
uv run spec-forge validate <dir>                              # quality gates
uv run spec-forge deploy   <dir>                              # root symlinks for tool discovery
uv run spec-forge status   <dir>                              # lifecycle progress
uv run spec-forge export   <dir>                              # single timestamped PDF of all spec files (for team review)
```

- **Stacks:** `python` · `node` · `go` (pluggable stack profiles).
- **Backends:** `mock` (offline, deterministic — default) · `claude` (Anthropic Messages
  API, `claude-opus-4-8`; needs `ANTHROPIC_API_KEY` or an `ant` profile).
- **Re-spec:** re-running a phase shows a diff and asks before overwriting (`--yes` to skip).

## Develop

```bash
uv run ruff check .
uv run pytest --cov=spec_forge
```

## How it's built

app-first **hybrid**: a deterministic engine does the structure/lifecycle/validation; AI
personas fill the content. This tool's own requirements live in [`specifications/`](specifications/) —
written with its own spec-driven process (dogfooding).
