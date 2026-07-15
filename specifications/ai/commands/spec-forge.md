---
description: Exact spec-forge subcommands natively in Claude Code (spec/plan/tasks/analyze/fill…), on the subscription
argument-hint: <subcommand> [arguments] — spec | plan | tasks | analyze | fill | init | validate | export | deploy | status
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash, TodoWrite, TaskCreate, TaskUpdate, TaskList
---
<!-- spec-forge-command v6 -->

You are the **dispatcher** `/spec-forge <subcommand> [arguments]`. The **first token** of `$ARGUMENTS` is the
subcommand (the same set as in the `spec-forge` CLI). Run EXACTLY the corresponding functionality in the
`specifications/` directory of the current project. Don't guess "the target in your own words" — route by subcommand.

Two classes of subcommands:
- **Content** (`spec`, `plan`, `tasks`, `analyze`, `fill`) — generate **natively here**, in Claude Code, via
  role subagents (`Task`). Do NOT call the CLI — content is generated here, on the Claude subscription.
- **Mechanical / deterministic** (`init`, `validate`, `export`, `deploy`, `status`) — run the local
  CLI: in the terminal `spec-forge $ARGUMENTS`, show the output. They are free and deterministic. If
  `spec-forge` is not found (`command -v spec-forge`) — say how to install it, and stop.

## Routing

### `spec [description]` — BA → `specifications/product/specs/001-feature/spec.md`
If inputs are missing — briefly clarify in the dialogue (a subagent can't ask the user) and close out
`[NEEDS CLARIFICATION]`. Then delegate to `Task` (subagent_type: `business-analyst`) with a **full brief**
→ spec.md: EARS / Given-When-Then, testable user stories (P1 = MVP), measurable success criteria,
glossary. **Gate.**

### `plan` — SA → `specifications/architecture/plan.md`
Read spec.md. `Task` (subagent_type: `solution-architect`) → `architecture/plan.md` + ADR in
`architecture/decisions/` + contracts `contracts/openapi.yaml` (asyncapi.yaml if needed), NFR in numbers. **Gate.**

### `tasks` — Developer → `specifications/delivery/tasks.md`
Read plan.md. `Task` (subagent_type: `developer`) → atomic, traceable tasks. **Gate.**

### `analyze [directory]` — brownfield: spec from code + doc-drift audit (in-place, we don't touch the code)
The target is the directory from `$ARGUMENTS` (default `.`). Delegate to `Task` (subagent_type: `reverse-analyst`) — it
reads the target's code itself (skipping `node_modules`, `.venv`, `.git`, binary/large files) →
`specifications/product/specs/002-existing/spec.md` (the actual spec, with references to files). Then
`Task` (subagent_type: `reviewer`) — give it both the existing docs `specifications/` and the code: it **reconciles the docs
against the code**, finds what is missing/deficiencies and **drift** (code changed, docs didn't) → `.../002-existing/review.md`
with **concrete doc-rewrite options** (don't apply them without confirmation). **Gate.**

### `fill` — step-by-step wizard: fill ALL `specifications/` files (native, with a progress checklist)
The target is the current project's `specifications/` (if there's no bundle — run `init` first). Mode: **auto-draft → confirmation**.

1. **Build a live checklist** (the right-hand todo panel): `TodoWrite` (or `TaskCreate`/`TaskUpdate` — whichever is available),
   one item per **content** file of the bundle, in dependency order:
   `00-constitution.md` → `product/specs/**/spec.md` → `architecture/plan.md` → `architecture/decisions/*` →
   `contracts/*` → `architecture/nfr.md` → `delivery/tasks.md` → `design/*` → `roles/*` → `knowledge/*` → `README.md`.
   Mark purely **config/deterministic** files (`.editorconfig`, `mcp.json`, `settings.json`, `tool-versions`,
   `gitattributes`, `editors/*`, `hooks/*`) as "scaffolded ✅ (skip)" — we don't fill those via interview.
2. **Go step by step.** For each file (item → in-progress):
   - read the project's code (`Read`/`Grep`/`Glob`) and the **accumulated answers from previous steps**;
   - **draft it yourself** (`Write`/`Edit`), consistent with the code and the already-filled files; where input is missing — `[NEEDS CLARIFICATION]`;
   - show what you wrote, and **stop for confirmation** — the user accepts/edits (gate);
   - update the item → ✅ and move on to the next.
3. Each user answer is **context for the next steps**: don't ask twice for what's already known;
   make suggestions based on what came before. At the end run `spec-forge validate` (all gates green).

Delegate the heavy parts (spec/plan/tasks) to the appropriate subagent (`Task`) when needed, but **put the accumulated context into the brief**.

### `init` / `validate` / `export` / `deploy` / `status`
Run `spec-forge $ARGUMENTS` in the terminal and show the output (deterministic, local).

### empty or `help`
Show the list of subcommands above (one description line per subcommand) and stop.

Rules: when delegating, provide a self-contained brief (the subagent doesn't see this dialogue); a human gate after
each content phase; a repeat run = update, not a duplicate; don't change the project's code without a separate request.
