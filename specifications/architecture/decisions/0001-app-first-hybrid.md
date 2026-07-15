# ADR-0001: App-first hybrid, modular monolith with plugin seams

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** SA (+ human)

## Context
We need a tool that generates a quality spec for **any** project. The forks:
pure app / pure subagent / hybrid; monolith / microservices; hardcoded stack / plugins.

## Decision
- **App-first hybrid:** a deterministic CLI engine + AI subagents for content.
- **Modular monolith:** a single process, modules with contractual boundaries.
- **Plugin seams:** `AIBackend` and `StackProfile` are interfaces; the MVP implementations are `MockBackend`
  (real content — native Claude Code subagents) and the python/node/go profiles.

## Consequences
**Positive**
- Determinism of structure, testability, low cost, clarity.
- A new stack/backend is added without core changes.
- Intelligence is plugged in surgically — where it actually pays off.

**Negative / trade-offs**
- A hybrid = two paradigms (code + prompts) — the boundary between them must be kept clean.
- LLM variability in the content phases (we mitigate it with validators + a human gate).

## Alternatives considered
- **Pure subagent** — rejected: variability, the need for an LLM at every step, hard to guarantee the output.
- **Pure app (no AI)** — rejected: cannot produce content (requirements, ADR, trade-offs).
- **Microservices** — rejected: a local CLI, distribution is unnecessary; seam modules are enough.
