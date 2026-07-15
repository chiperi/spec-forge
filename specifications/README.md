# specifications/

> ✅ **READY-TO-USE TEMPLATE (v1 · 2026-07).**
> A new project = a copy of this directory. Automatically: `../new-project.sh <target-dir>`
> (copies `specifications/` into the project and creates root symlinks for tool discovery).

📌 **A single hierarchy** of all of the project's specification and configuration artifacts.
In a real project this is one `specifications/` directory, not files scattered across the root.
Derived from the baseline `../spec-template-tree/` (which is an annotated reference/superset).

## Structure (by layers / roles)

```
specifications/
├── 00-constitution.md            project principles (highest level)
├── ai/                           🤖 context, config, and agent CAPABILITIES
│   ├── AGENTS.md                 ⭐ THE single source of truth
│   ├── CLAUDE.md → AGENTS.md     GEMINI.md → AGENTS.md   (symlink)
│   ├── settings.json             permissions · model · hooks (in git)
│   ├── settings.local.json.example  personal (gitignored)
│   ├── rules/                    user-rules.md · copilot-instructions.md
│   ├── agents/                   persona subagents (BA/SA/designer/developer + reverse-analyst/reviewer)
│   ├── commands/                 custom slash commands
│   ├── skills/                   skills (SKILL.md by trigger)
│   ├── hooks/                    event scripts (guardrails; run by the harness)
│   ├── mcp/                      MCP servers = external tools (→ .mcp.json)
│   └── editors/                  per-editor rules (cursor/windsurf/junie/cline/aider)
├── product/                      👤 BA — WHAT/WHY
│   ├── glossary.md
│   └── specs/001-example-feature/{spec,research,data-model,quickstart}.md
├── architecture/                 🏛️ SA — HOW
│   ├── plan.md · nfr.md · fitness-functions.md · threat-model.md
│   ├── observability.md · traceability-matrix.md · constitution.md
│   └── decisions/0001-*.md       (ADR)
├── contracts/                    🔌 openapi.yaml · asyncapi.yaml
├── services/                     🧩 micro/hybrid: service-catalog.md + example-service/
├── design/                       🎨 Designer — flows/states/a11y
├── delivery/                     🛠️ Developer — tasks.md
├── quality/                      ✅ workflows/* · pre-commit · spectral
├── platform/                     💻 OS/cross-platform (deployed to root as dotfiles)
├── roles/                        👥 role guides (for people)
└── knowledge/                    🧠 domain knowledge
```

## Flow (spec-driven)
`00-constitution` → `product/specs` (BA) → `architecture/plan` + `decisions` + `contracts` (SA)
→ `design/` (Designer) → `delivery/tasks` (Developer) → `quality/` gates.

## Deploying to the project root (tool discovery)
Some files are looked up by tools at fixed paths. The source of truth stays here,
and we place a **symlink** (or a copy) in the root. Example (from the project root):

```bash
ln -s specifications/ai/AGENTS.md AGENTS.md
ln -s specifications/ai/AGENTS.md CLAUDE.md
ln -s specifications/ai/mcp/mcp.json .mcp.json
mkdir -p .claude
ln -s ../specifications/ai/agents   .claude/agents
ln -s ../specifications/ai/commands .claude/commands
ln -s ../specifications/ai/skills   .claude/skills
ln -s ../specifications/ai/hooks    .claude/hooks
ln -s ../specifications/ai/settings.json .claude/settings.json
mkdir -p .github && ln -s ../specifications/ai/rules/copilot-instructions.md .github/copilot-instructions.md
ln -s ../specifications/quality/workflows .github/workflows
ln -s specifications/platform/editorconfig  .editorconfig
ln -s specifications/platform/gitattributes .gitattributes
ln -s specifications/platform/tool-versions .tool-versions
```

> Three senses of the word **"tools"**: (1) `mcp/` — external tools (MCP servers); (2) the `tools:` field in
> `agents/*.md` — which built-in tools a subagent is allowed to use; (3) `allow/deny` in `settings.json` —
> tool permissions. `editors/` is NOT tools, but rules for specific editors.

Theory for each block is in the adjacent `../notes/` directory.
