# hooks/

Event-driven scripts (registered in `settings.json` → `hooks`).
Events: PreToolUse · PostToolUse · Stop · UserPromptSubmit · SessionStart, etc.
They are run by the HARNESS (not the model) — so they suit hard guardrails:
format/lint after edits, prohibitions, notifications.
