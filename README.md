# spec-forge

Stack-agnostic, spec-driven development CLI: turn any project into a complete,
**AI- & OS-friendly specification bundle**. Deterministic scaffolding + Claude-powered
drafting across BA / SA / Developer personas, quality gates, lifecycle state, and
one-command tool-discovery deploy.

## Install

```bash
uv sync
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
