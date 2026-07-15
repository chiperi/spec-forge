# roles/ — role instructions

Role instructions for the team (people **or** AI agents playing a role). Each file = one persona:
who they are, what they do, which artifact they deliver, what they do **not** do, and whom they hand off to.

This maps directly onto the spec-driven cycle:

```
Business Analyst → spec.md            (WHAT/WHY, requirements)
        ↓
Solution Architect → plan.md + decisions/ + contracts/   (HOW, architecture, NFR, contracts)
        ↓                    ↘
Designer → design/ (UX/UI)    Developer → src/ + tests/ (implementation per tasks.md)
```

| Role | File | Owns artifact |
|------|------|--------------------|
| Business Analyst | [business-analyst.md](business-analyst.md) | `spec.md`, glossary |
| Solution Architect | [solution-architect.md](solution-architect.md) | `plan.md`, `decisions/`, `contracts/`, NFR |
| Designer (UX/UI) | [designer.md](designer.md) | design specs, a11y |
| Developer | [developer.md](developer.md) | `src/`, `tests/`, `tasks.md` |

## How to apply
- **As a guide for people** — read by whoever plays the role.
- **As an AI subagent** — copy the essence into `.claude/agents/<role>.md` (frontmatter + prompt) and invoke it for the task.
- The key part of each file is the **boundaries**: what the role does NOT do (so the agent doesn't "sprawl").
