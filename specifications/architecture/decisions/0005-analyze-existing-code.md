# ADR-0005: `analyze` — reverse spec + review of existing code

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer (+ SA)

## Context
Greenfield mode drafts from a description (`-d`) + `AGENTS.md`, **without reading the code**. We need brownfield:
from existing code, produce (1) a reverse spec (what it does) and (2) a review (where/what to fix, whether everything is as it should be).

## Decision
- A single command **`analyze <source>`**: one code scan → two documents (`--only both|spec|review`).
- **In-place:** writes to `<source>/specifications/product/specs/002-existing/{spec,review}.md`
  (`--path` / `--slug` — override). **Does not touch the code.**
- **`init` is not needed** (brownfield): the directories are created by `_write_artifact`.
- The code reader **`codescan.py`** — a curated ignore-set (without `.gitignore`/`pathspec`): deterministic,
  offline, tested; limits `--max-file-bytes` / `--max-chars`.
- Two new personas: **`reverse-analyst`**, **`reviewer`**.
- The `analyze` / `review` phases — via `mark_phase`/`phase_done` (re-spec diff/confirm), but **NOT** in `state.PHASES`
  (so as not to change `status`/`validate`).

## Consequences
**Positive**
- Reuse of `_run_phase` / `_write_artifact` / `_read_first_spec`; no new dependency.
- The reverse spec is first-class: it is seen by `validate` / `export` / `plan`.

**Negative / trade-offs**
- The real content — natively via `/spec-forge analyze` (Claude Code); the CLI `analyze` is an echo
  (test/offline scaffold).
- `.gitignore` is not parsed — deferred (a future `--gitignore` + `pathspec`).
- Large repos are truncated by `--max-chars` (the subagent's context limit).
