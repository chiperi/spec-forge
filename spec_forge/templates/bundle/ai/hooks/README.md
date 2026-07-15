# hooks/

Event-driven scripts (registered in `settings.json` → `hooks`).
Events: PreToolUse · PostToolUse · Stop · UserPromptSubmit · SessionStart, etc.
The HARNESS runs them (not the model) — so they suit hard guardrails:
format/lint after edits, prohibitions, notifications.
