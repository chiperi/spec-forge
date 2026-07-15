# Glossary (Ubiquitous Language) — spec-forge

Unified project terminology: one word = one meaning.

| Term | Definition | Context |
|--------|-----------|----------|
| **Spec bundle** | The full `specifications/` directory with all layers — the tool's output artifact | output |
| **Stack profile** | Stack plugin: linters, task-runner, test framework, Docker base, version pinning | stack independence |
| **Phase** | Lifecycle step: spec → plan → design → tasks → validate → deploy | process |
| **Persona / subagent** | Role that populates artifacts: BA / SA / Designer / Developer | content generation |
| **Gate** | A human confirmation point between phases | human-in-the-loop |
| **Quality gate** | Automated quality check of the spec itself (completeness, measurability, contract linting) | validation |
| **Engine** | The deterministic part: scaffolding, rendering, state, validation, symlinks | CLI |
| **Deploy** | Creating root symlinks for tool discovery (AGENTS.md, .claude/…) | deployment |
