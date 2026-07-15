# ADR-0006: Native `/spec-forge` — a dispatcher of exact subcommands (on subscription)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer

## Context
The thin `/spec-forge` wrapper simply launched the CLI. We need a native flow that performs **the same
functionality as the CLI**, generating content directly in Claude Code with role subagents
(on a **Claude Max** subscription).

## Decision
- Rewrite `_WRAPPER` into a **dispatcher of exact subcommands** (`v3`): `/spec-forge <subcommand>` maps
  to the same set as the CLI. The **content** subcommands (`spec`/`plan`/`tasks`/`analyze`) run
  natively in Claude Code by delegating to role subagents (`Task`); the **mechanical** ones (`init`/`validate`/
  `export`/`deploy`/`status`) — to the local CLI (deterministic, free). A human gate after the content phase.
  > History: `v2` was a conversational orchestrator that "guessed the target in its own words"; `v3` switched to
  > exact subcommands at the user's request — so that `/spec-forge plan`, `/spec-forge analyze` invoke
  > exactly the implemented functionality.
- Content — everything on the **Claude Max subscription** (natively in Claude Code); the mechanical subcommands — via
  the already-installed CLI.
- Install **6 role subagents** in `~/.claude/agents/` (so that delegation works in any
  project); the source is `spec_forge/templates/bundle/ai/agents/*.md`. For `analyze`, `reverse-analyst`
  (the actual spec) and `reviewer` (gap/review) were added, mirroring the personas of the CLI's `analyze` mode (ADR-0005).
- **Self-upgrade** of the command by a version marker (`<!-- spec-forge-command vN -->`);
  `command install --force` updates the command + the agents.
- Extends ADR-0004 (auto-provision).

## Consequences
**Positive**
- Works **on the Claude Max subscription**; content is generated natively by role personas.
- `/spec-forge <subcommand>` = exact, predictable CLI functionality, not a free interpretation of text.
- The subagents are available globally — the flow works in any project.

**Negative / trade-offs**
- The mechanical subcommands depend on the presence of the local `spec-forge` CLI (a `command -v` check;
  if it is absent — the command asks to install it and stops).
- Installing the command/agents is still via `command install` / auto-callback (one-time); a separate
  Claude Code plugin (plugin.json + marketplace) is out of scope.
- The subagents are non-interactive (a separate thread) → clarifications in the main thread, delegation with a full brief.
