# Tasks: spec-forge

**Based on:** `../architecture/plan.md`
> Atomic, traceable tasks. `[P]` — can be done in parallel. `[x]` — done in this increment.

## Wave 1 — Project skeleton
- [x] **T-001** uv project: `pyproject.toml`, entry point `spec-forge`, deps (typer/jinja2/pydantic) + dev (pytest/ruff)
- [x] **T-002** [P] `spec_forge/` package structure (cli, models, profiles, backends, scaffolder, templates)
- [x] **T-003** [P] models (`InterviewAnswers`, `Phase`)

## Wave 2 — Deterministic engine + init (US-1, FR-001/002/007)
- [x] **T-004** `StackProfile` interface + python/node/go profiles
- [x] **T-005** `scaffolder` + Jinja2 rendering (sorted traversal, no time/random → NFR-002/003)
- [x] **T-006** CLI `init`: scaffold + interview (flags + prompts), guard against an existing bundle
- [x] **T-007** tests: scaffolder (determinism/completeness/guard) + `init` (SC-002/003)

## Wave 3 — spec phase (US-2, FR-003) — AI seam
- [x] **T-008** `AIBackend` interface + `MockBackend`
- [x] **T-009** CLI `spec`: draft via backend + tests
- [x] **T-010** BA persona (persona prompts)
- [x] **T-011** `[NEEDS CLARIFICATION]` validation in spec (in `validators`)

## Wave 4 — Phases + validation + deploy (US-3/4/5/6, FR-004/005/006/008)
- [x] **T-012** `validators`: structure · clarifications · measurable-success (contract-lint — TODO, once OpenAPI exists)
- [x] **T-013** CLI `validate` (exit 1 on a gate failure)
- [x] **T-014** CLI `deploy` (root symlinks; existence-guarded)
- [x] **T-P1** CLI `plan` (SA persona → `architecture/plan.md`)
- [x] **T-P2** CLI `tasks` (developer persona → `delivery/tasks.md`)

## Wave 5 — Later (P2/P3)
- [x] **T-015** full layout template (ai config · platform · quality · roles · knowledge · contracts · services) + stack-dependent `tool-versions` + CLAUDE/GEMINI symlinks
- [x] **T-016** re-spec: diff + confirmation on re-running a phase (FR-012 / US-8); `--yes` for CI
- [x] **T-017** lifecycle state `.spec-forge/state.json` + `status` command (FR-009)
- [x] **T-018** CI (`.github/workflows/ci.yml`): matrix ubuntu/macos/windows, ruff + pytest, coverage ≥85% (NFR-006)

- [x] **T-019** `export` — PDF snapshot of all `specifications/` files (timestamp, `exports/` directory) via fpdf2 + embedded DejaVuSans (FR-013/US-9, ADR-0003)
- [x] **T-020** auto-registration of the Claude Code slash command `/spec-forge` + `command install/uninstall` (FR-014/US-10, ADR-0004)
- [x] **T-021** `analyze` — brownfield: `codescan` (limited code reader) + `reverse-analyst`/`reviewer` personas + reverse spec + in-place review (FR-015/US-11, ADR-0005)
- [x] **T-022** `/spec-forge` v3 — **dispatcher of exact subcommands** (spec/plan/tasks/analyze natively; init/validate/… via CLI), on the subscription (FR-016/US-12, ADR-0006)
- [x] **T-023** installing 7 role subagents in `~/.claude/agents/` (+ `reverse-analyst`/`reviewer` for analyze) + self-upgrade + `command install --force` (FR-017)
- [x] **T-024** tests install/remove/dispatcher-markers/self-upgrade/enumeration
- [x] **T-025** docs: ADR-0006 + README section
- [x] **T-026** `reverse-analyst` + `reviewer` subagents (`ai/agents/` bundle) for native `/spec-forge analyze`
- [x] **T-027** PDF export: emoji icons via the fallback font `NotoEmoji.ttf` (monochrome, OFL) + `set_fallback_fonts` (ADR-0003)
- [x] **T-029** `/spec-forge fill` — native wizard for step-by-step filling of all `specifications/` files
  (auto-draft → confirmation, live todo checklist, context accumulation across steps); wrapper v6 + todo tools (FR-018/US-13)

---
**ALL tasks (T-001…T-027, T-029 + phases) are done.** Commands: `init · spec · plan · tasks · analyze · validate · deploy · status · export · command`; `fill` — native wizard in Claude Code.
`/spec-forge <subcommand>` — a dispatcher of exact subcommands (content natively on the subscription, mechanical via CLI). 49 tests, ruff clean.
