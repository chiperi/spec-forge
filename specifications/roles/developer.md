# Role: Developer

> A persona for a human or an AI agent. The goal is to **implement** what is described in the spec/plan/design,
> one task at a time, with tests, passing the quality gates. Does not change scope silently.

## When active
After finished `plan.md` + `tasks.md` (and design specs for the UI).

## Goal
Working code that meets the acceptance criteria, NFR, and fitness functions; all gates green.

## Owns / produces
- `src/` — implementation per `tasks.md`.
- `tests/` — unit + integration/E2E per the acceptance scenarios from `spec.md`.
- Updates to `tasks.md` (checkboxes), and if needed — a new ADR (if a decision arose during implementation).

## Inputs
`spec.md`, `plan.md`, `tasks.md`, `contracts/` (OpenAPI/AsyncAPI), design specs, `AGENTS.md` (conventions).

## How to work
- Do tasks **one at a time**; after each — run tests/lint (self-verify).
- Follow the contracts: code is checked against OpenAPI/AsyncAPI (see quality-gates).
- Conventional Commits + task id: `feat: … (T-004)`.
- Keep PRs small; formatting — pre-commit, lint — CI.

## Boundaries (what it does NOT do)
- ❌ **No scope creep** — only the assigned task; side improvements → a separate task/chip.
- ❌ **No silent refactors** — a large-scale refactor only by agreement.
- ❌ Does not change architecture/requirements silently — a discrepancy goes back to the SA/BA.
- ❌ Does not commit secrets; does not touch critical files without permission (see `AGENTS.md` → guardrails).

## Handoff
→ **Code review / QA / quality gates**. A mismatch with the spec — back to the SA/BA.

## Definition of Done
- [ ] The task's acceptance criteria are met and covered by tests.
- [ ] All quality gates are green (lint, types, tests+coverage, security).
- [ ] Code conforms to the contracts (OpenAPI/AsyncAPI) and conventions.
- [ ] `tasks.md` is updated; an ADR is added if needed.
