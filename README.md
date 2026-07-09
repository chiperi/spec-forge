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

## Analyze an existing project (brownfield)

Point spec-forge at an existing codebase to reverse-engineer its spec **and** a review/gap report —
without touching the code:

```bash
spec-forge analyze /path/to/existing-project --backend claude
# → <project>/specifications/product/specs/002-existing/spec.md   (what it does today)
# → <project>/specifications/product/specs/002-existing/review.md  (where/what to fix, is it correct)
```

- `--only both|spec|review` · `--slug <name>` · `--path <dir>` (write elsewhere) · `--max-chars` / `--max-file-bytes`.
- Skips `node_modules`, `.venv`, `.git`, binaries, oversized files. No `init` required.
- `--backend mock` scaffolds offline (echo); real analysis needs `--backend claude` + `ANTHROPIC_API_KEY`.

## Claude Code integration — conversational `/spec-forge` (no API key)

On first run, spec-forge registers a Claude Code slash command **and 5 role subagents**
(`business-analyst`, `solution-architect`, `designer`, `developer`, `code-reviewer`) under `~/.claude/`.
Then `/spec-forge <goal>` builds the spec **conversationally, natively in Claude Code**: it interviews
you, delegates drafting to the role subagents, and writes files into `specifications/`. It runs on your
Claude subscription — **no `ANTHROPIC_API_KEY` / API credits needed** (the API path is only for the CLI
`--backend claude`).

Flow: **BA** (interview → `spec.md`) → gate → **SA** (`plan.md` + ADRs + contracts) → gate → optional
**Designer** / **Developer** (tasks). Reload Claude Code after install to see `/spec-forge`.

- Install / refresh: `spec-forge command install [--project] [--force]` · remove: `spec-forge command uninstall`.
- Opt out of auto-registration: `export SPEC_FORGE_NO_SLASH=1`.
- The command self-upgrades to the latest version on the next CLI run.

> Python/uv has no uninstall hooks, so `uv tool uninstall` can't auto-remove them — run
> `spec-forge command uninstall`.

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
