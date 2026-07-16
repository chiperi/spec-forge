# Security policy

spec-forge is a deterministic, offline CLI plus a Claude Code slash command. It stores no credentials: real AI content is generated natively in Claude Code on your own subscription, and the standalone CLI makes no network calls of its own.

## Supported versions

This is a pre-1.0 personal project. Only the latest `main` is supported — fixes land there.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Instead, use GitHub's private reporting: the repo's **Security** tab → **Report a vulnerability** (private vulnerability reporting). Include steps to reproduce and the affected version or commit.

Response is best-effort (personal project). Once a fix is ready it lands on `main`, and you will be credited if you wish.

## Scope notes

- Never include secrets, tokens, or a real `.env` in issues, PRs, or commits.
- `.gitignore` already excludes `.env`, local state (`.spec-forge/`), and `exports/` — keep it that way.
