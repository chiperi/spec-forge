# AGENTS.md — spec-forge

> ⭐ The SINGLE source of truth for all AI agents. `CLAUDE.md`/`GEMINI.md` → symlink to this file.

## Project overview
**spec-forge** — a CLI tool that generates a high-quality, portable, AI/OS-friendly specification
(`specifications/` bundle) for **any** project and stack. A hybrid: a deterministic engine
(scaffolding + lifecycle + validation) + AI subagents (BA/SA/Designer/Developer) for content filling.
The full product spec is in `../product/specs/001-spec-generation/spec.md`.

## Tech stack
- Language / runtime: **Python 3.12+** (type hints)
- CLI: **Typer**
- Package manager: **uv**
- Tests: **pytest** (+ coverage)
- Lint/format: **Ruff**
- AI content filling: **natively in Claude Code** via `/spec-forge` subagents (on a Claude subscription); the CLI backend is a deterministic `mock`
- The tool's output (spec bundle) is **stack-agnostic**: the target stack is set by a stack-profile, not hardcoded.

## Setup commands
```bash
uv sync            # install dependencies
uv run spec-forge  # run the CLI
uv run pytest      # tests
uv run ruff check  # lint
uv run ruff format # format
```
> Baseline values; refined in the SA phase (`plan.md`).

## Code style
- Ruff (lint + format); type hints are mandatory; no `any`-like loopholes.
- The engine core is deterministic and tested; no hardcoding of a specific stack in the core.

## Testing
- Unit — the engine (scaffolding, rendering, validators); the coverage threshold is refined in the NFR.
- Determinism: identical inputs → identical output (verified in CI, matrix across OSes).

## Workflow
Spec first (`product/specs/`), then architecture (`architecture/plan.md` + `decisions/`), then code.
Phases with a human gate between them. Important decisions → ADR in `../architecture/decisions/`.

## Security & guardrails
- Do not commit secrets / `.env`.
- Do not silently change the bundle structure — it is a template artifact.
- No large-scale refactorings "along the way" — only the task at hand.
