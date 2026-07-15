# Product Specification: spec-forge

**Feature Branch:** `001-spec-generation`
**Created:** 2026-07-09
**Status:** Ready (BA gate passed)
**Author:** BA (business-analyst persona)

> BA phase: WHAT and WHY. The technical "how" lives in `../../../architecture/plan.md` (SA phase).

---

## 1. Problem & context

Teams building software with AI agents write specs **ad hoc and inconsistently**: prompts
get thrown away, the format differs across OSes and across tools (Claude/Cursor/Copilot), and on complex
projects there is a lack of quantified NFRs, contracts, threat models, and traceability. There is no single way
to reliably produce a **high-quality, portable, AI- and OS-friendly specification** for any stack.

## 2. Goals / Non-Goals

**Goals**
- Generate a complete, high-quality `specifications/` bundle for **any** project and stack.
- Hybrid: deterministic structure (engine) + AI-generated content (subagents).
- Check the quality of **the spec itself** (completeness, measurability) through quality gates.
- Portability: identical results across OSes and compatibility with different AI tools.

**Non-Goals**
- ❌ Does not write application code (that is downstream / Developer).
- ❌ Not a general-purpose project/task management system.
- ❌ Not tied to a single stack or a single AI vendor (architecturally — via abstractions).

---

## 3. User Scenarios & Testing

### US-1 — Project initialization (Priority: P1)
As a **developer/architect**, I want to run `spec-forge init` and go through an interview, so that I get
a complete `specifications/` skeleton tailored to my project and stack.
- *Why P1:* without a skeleton there is nothing to work with — this is a self-sufficient MVP.
- *Independent Test:* running `init` in an empty directory → a valid `specifications/` bundle.

**Acceptance Scenarios**
- **Given** an empty directory, **When** I run `init` and answer the questions, **Then**
  `specifications/` is created with all layers and the applied stack profile.
- **Given** a directory where `specifications/` already exists, **When** I run `init`, **Then** I get an error
  and nothing is overwritten (for updates — use re-spec mode, US-8).

### US-2 — Requirements draft, BA (Priority: P1)
As a **user**, I want the tool to run an interview and compose `product/specs/*/spec.md`, so that the requirements
are in EARS/Given-When-Then with **measurable** success criteria.
- *Independent Test:* after `init` → `spec-forge spec` → `spec.md` is created, and the validator catches
  missing acceptance / non-measurable criteria.

**Acceptance Scenarios**
- **Given** init is done, **When** `spec-forge spec`, **Then** `spec.md` is populated, and `validate`
  flags all open `[NEEDS CLARIFICATION]`.

### US-3 — Architecture draft, SA (Priority: P2)
As a user, I want `spec-forge plan`, so that I get `plan.md` + ADR + contracts (OpenAPI/AsyncAPI)
+ NFR + threat model.
**Acceptance:** **Given** a ready spec.md, **When** `plan`, **Then** a plan is created with quantified NFRs and
contracts that pass the spectral lint.

### US-4 — Task derivation (Priority: P2)
As a user, I want `spec-forge tasks`, so that I get `delivery/tasks.md` — atomic, traceable tasks.

### US-5 — Bundle validation (Priority: P2)
As a user, I want `spec-forge validate`, so that I can run the quality gates across the whole spec and see the gaps.

### US-6 — Deployment (Priority: P3)
As a user, I want `spec-forge deploy`, so that I get root symlinks for tool discovery.

### US-7 — Stack independence (Priority: P2)
As a user of any stack, I want to choose a stack profile (python/node/go…), so that the `platform/` files
match my stack — without changing the tool's core.

### US-8 — Updating an existing spec / re-spec (Priority: P3)
As a user, I want to update an existing bundle (`spec-forge <phase> --update`), so that I can make changes
without losing manual edits.
**Acceptance:** **Given** an existing bundle with manual edits, **When** I run re-spec, **Then**
the changes are merged, the manual edits are preserved, and a diff is shown for confirmation before writing.

### US-9 — PDF snapshot for review (Priority: P3)
As a **team**, we want `spec-forge export`, so that we get a single PDF of all specification files
(with a timestamp) — to open, proofread, and mark which files need changes.
**Acceptance:** **Given** there is a bundle, **When** `export`, **Then** in `exports/` a
`spec-forge-export-<timestamp>.pdf` is created with all text files from `specifications/`.

### US-10 — Claude Code slash command (Priority: P3)
As a Claude Code user, I want to invoke `/spec-forge …` in chat, and have the wrapper appear/disappear
together with the tool.
**Acceptance:** **Given** the tool is installed, **When** the CLI runs for the first time, **Then**
`~/.claude/commands/spec-forge.md` is created; `spec-forge command uninstall` removes it.

### US-11 — Analyzing an existing project (Priority: P2)
As a developer, I want `spec-forge analyze <project>`, so that from existing code I get a spec (what it does)
and a review that **reconciles the docs with the code**: what is missing, deficiencies, and drift (code changed — docs did not), with
concrete options for rewriting the docs.
**Acceptance:** **Given** a directory with code, **When** `/spec-forge analyze` (real content, native)
or `spec-forge analyze` (deterministic CLI scaffolding), **Then** in
`specifications/product/specs/002-existing/` `spec.md` and `review.md` are created with references to files.

### US-12 — `/spec-forge` subcommands natively, on the subscription (Priority: P1)
As a Claude Max user, I want to invoke **exact subcommands** —
`/spec-forge spec`, `/spec-forge plan`, `/spec-forge analyze`, etc. — so that I can run exactly that
functionality right inside Claude Code via subagents.
**Acceptance:** **Given** the command + subagents are installed,
**When** `/spec-forge plan` (or `spec`/`tasks`/`analyze`), **Then** the dispatcher delegates to the appropriate
subagent and writes the artifact into `specifications/` — natively on the Claude subscription; **When** `/spec-forge validate`
(or `init`/`export`/`deploy`/`status`), **Then** the local CLI runs.

### US-13 — Step-by-step bundle-fill wizard (Priority: P2)
As a Claude Code user, I want `/spec-forge fill`, so that I can fill all the `specifications/` files
**step by step**: at each step the agent drafts the file itself (from the code + **accumulated answers
from previous steps**), I confirm/edit, and a **live checklist** (todo panel) shows ✅/unfilled.
**Acceptance:** **Given** there is a `specifications/` bundle, **When** `/spec-forge fill`, **Then** a
todo checklist is built for each content file and each is drafted in turn (auto-draft) with a confirmation
gate; config files are marked "scaffolded (skip)"; anything already known from previous steps is not asked again.

### Edge Cases
- Open `[NEEDS CLARIFICATION]` items **block** moving to the next phase.
- Re-running a command is **idempotent** (does not duplicate or corrupt artifacts).
- The directory is not a git repository.
- No AI backend available for the content phases → a clear error, and the deterministic part still works.
- Re-spec over a file with conflicting manual edits → show a diff, do not overwrite blindly.

---

## 4. Requirements

### Functional Requirements
- **FR-001:** The system MUST scaffold the `specifications/` bundle with all defined layers.
- **FR-002:** The system MUST conduct a structured interview (domain, goals, constraints, stack, architecture style).
- **FR-003:** The system MUST compose `spec.md` via the BA persona in EARS / Given-When-Then format.
- **FR-004:** The system MUST compose `plan.md`, ADRs, contracts (OpenAPI/AsyncAPI), NFRs, and a threat model via the SA persona.
- **FR-005:** The system MUST derive an atomic, traceable task list.
- **FR-006:** The system MUST validate the bundle against the quality gates (completeness, measurable NFRs, no open clarifications, contract linting).
- **FR-007:** The system MUST support pluggable stack profiles **without core changes**.
- **FR-008:** The system MUST deploy root pointers (symlinks) for tool discovery.
- **FR-009:** The system MUST require human confirmation between phases (gate).
- **FR-010:** The system MUST perform real AI content generation for the phases **natively in Claude Code** via
  role subagents (`/spec-forge`, on the Claude subscription). The standalone CLI provides only
  **deterministic `mock` scaffolding** through the abstract `AIBackend` interface.
- **FR-011:** The CLI MUST support **flags** (for automation/CI) and **interactive prompts**
  (when a value is not provided), based on Typer. A full TUI is out of scope for the MVP.
- **FR-012:** The system MUST support **re-spec** mode — updating an existing bundle while
  preserving manual edits (merge + diff confirmation, without blind overwriting).
- **FR-013:** The system MUST export all `specifications/` files into a **single PDF** (name with
  a timestamp, a dedicated `exports/` directory) for team review.
- **FR-014:** The system MUST automatically register the Claude Code slash command `/spec-forge`
  on first run (idempotently) and provide a command to remove it; opt-out via `SPEC_FORGE_NO_SLASH=1`.
- **FR-015:** The system MUST have a brownfield `analyze` mode: read (in a limited way) an existing project's code,
  draft a **reverse spec** and a **docs-vs-code review** — a gap document that records what is missing,
  deficiencies, and **drift** (code changed, docs did not) and proposes options for rewriting the docs; in-place, without changing the code.
- **FR-016:** The system MUST provide `/spec-forge` as a **dispatcher of exact subcommands** (the same set
  as the CLI): content subcommands (`spec`/`plan`/`tasks`/`analyze`) run **natively in Claude Code** via
  role subagents (on the Claude subscription); mechanical ones (`init`/`validate`/`export`/
  `deploy`/`status`) are delegated to the local CLI. A human gate follows each content phase.
- **FR-017:** The system MUST install/remove role subagents in `~/.claude/agents/` together with the
  slash command (including `reverse-analyst`/`reviewer` for `analyze`); a **self-upgrade** command by version.
- **FR-018:** The system MUST provide a native `/spec-forge fill` wizard: step-by-step filling of **all**
  content files in `specifications/` in auto-draft → confirmation mode, with a **live todo checklist**
  of progress (filled/not) and **context accumulation** across steps (answers from previous steps are input for
  the next ones). Deterministic/config files are marked scaffolded (skip). Native only (Claude Code).

### Non-Functional (seed; details → `architecture/nfr.md`)
- **NFR-001:** The deterministic `init` scaffolding MUST complete in < 5 s on a typical project.
- **NFR-002:** The output MUST be identical on macOS/Linux/Windows given identical inputs.

### Key Entities
- **Project** — the target project (directory + metadata).
- **StackProfile** — a stack plugin (linters, task-runner, test framework, Docker, version pinning).
- **Phase** — spec / plan / design / tasks / validate / deploy.
- **Persona** — BA / SA / Designer / Developer (subagent).
- **Artifact** — a bundle file (spec.md, plan.md, ADR, contract…).
- **ValidationResult** — a quality-gate result (pass/fail + gaps).
- **AIBackend** — an abstraction over the content-generation backend (single implementation: `MockBackend`; real content generation — native Claude Code subagents).

---

## 5. Success Criteria (measurable)

- **SC-001:** A new user gets a **validated** spec bundle in < 30 min for a medium project.
- **SC-002:** 100% of generated bundles pass **structural** validation (no missing mandatory file).
- **SC-003:** In `spec.md` — **0** open `[NEEDS CLARIFICATION]` before the plan phase.
- **SC-004:** Works for **≥3 stacks** (python/node/go) via profiles **without core changes**.
- **SC-005:** Identical inputs → a **byte-identical** structure on 3 OSes.

---

## 6. Assumptions
- Real content generation is available via Claude Code (`/spec-forge`, subagents); the CLI works offline and deterministically.
- The bundle format = our `specifications/` template.
- The user approves each phase before the next one.

## 7. Open Questions

_BA-phase blockers closed (2026-07-09):_
- ✅ **AI backend:** real content generation — native Claude Code subagents; CLI — deterministic mock (FR-010).
- ✅ **Interface:** flags + interactive prompts, Typer (FR-011).
- ✅ **Re-spec:** we support updating an existing bundle (FR-012, US-8).

No open `[NEEDS CLARIFICATION]` → **the BA → SA gate is passed.**
