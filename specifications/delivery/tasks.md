# Tasks: spec-forge

**Based on:** `../architecture/plan.md`
> Атомарні, трасовані задачі. `[P]` — можна паралельно. `[x]` — зроблено в цьому інкременті.

## Wave 1 — Каркас проєкту
- [x] **T-001** uv-проєкт: `pyproject.toml`, entry point `spec-forge`, deps (typer/jinja2/pydantic) + dev (pytest/ruff)
- [x] **T-002** [P] структура пакета `spec_forge/` (cli, models, profiles, backends, scaffolder, templates)
- [x] **T-003** [P] моделі (`InterviewAnswers`, `Phase`)

## Wave 2 — Детермінований двигун + init (US-1, FR-001/002/007)
- [x] **T-004** `StackProfile` interface + профілі python/node/go
- [x] **T-005** `scaffolder` + Jinja2-рендер (сортований обхід, без часу/random → NFR-002/003)
- [x] **T-006** CLI `init`: scaffold + інтервʼю (флаги + prompts), guard на наявний bundle
- [x] **T-007** тести: scaffolder (детермінізм/повнота/guard) + `init` (SC-002/003)

## Wave 3 — spec фаза (US-2, FR-003) — AI seam
- [x] **T-008** `AIBackend` interface + `MockBackend` + `ClaudeBackend`
- [x] **T-009** CLI `spec`: чернетка через backend + тести
- [x] **T-010** BA-персона (промпти персон) + `ClaudeBackend` через Anthropic Messages API (ADR-0002)
- [x] **T-011** валідація `[NEEDS CLARIFICATION]` у spec (у `validators`)

## Wave 4 — Фази + валідація + деплой (US-3/4/5/6, FR-004/005/006/008)
- [x] **T-012** `validators`: structure · clarifications · measurable-success (contract-lint — TODO, коли буде OpenAPI)
- [x] **T-013** CLI `validate` (exit 1 при провалі гейта)
- [x] **T-014** CLI `deploy` (root symlinks; existence-guarded)
- [x] **T-P1** CLI `plan` (SA-персона → `architecture/plan.md`)
- [x] **T-P2** CLI `tasks` (developer-персона → `delivery/tasks.md`)

## Wave 5 — Пізніше (P2/P3)
- [x] **T-015** повний layout template (ai config · platform · quality · roles · knowledge · contracts · services) + stack-залежний `tool-versions` + symlinks CLAUDE/GEMINI
- [x] **T-016** re-spec: diff + підтвердження при повторному запуску фази (FR-012 / US-8); `--yes` для CI
- [x] **T-017** lifecycle-стан `.spec-forge/state.json` + команда `status` (FR-009)
- [x] **T-018** CI (`.github/workflows/ci.yml`): matrix ubuntu/macos/windows, ruff + pytest, coverage ≥85% (NFR-006)

- [x] **T-019** `export` — PDF-знімок усіх файлів `specifications/` (таймстемп, тека `exports/`) через fpdf2 + вбудований DejaVuSans (FR-013/US-9, ADR-0003)
- [x] **T-020** авто-реєстрація slash-команди Claude Code `/spec-forge` + `command install/uninstall` (FR-014/US-10, ADR-0004)
- [x] **T-021** `analyze` — brownfield: `codescan` (обмежений читач коду) + персони `reverse-analyst`/`reviewer` + reverse-спека + рев'ю in-place (FR-015/US-11, ADR-0005)
- [x] **T-022** `/spec-forge` v3 — **диспетчер точних підкоманд** (spec/plan/tasks/analyze нативно; init/validate/… через CLI), без API-ключа (FR-016/US-12, ADR-0006)
- [x] **T-023** встановлення 7 рольових субагентів у `~/.claude/agents/` (+ `reverse-analyst`/`reviewer` для analyze) + self-upgrade + `command install --force` (FR-017)
- [x] **T-024** тести install/remove/dispatcher-markers/self-upgrade/enumeration
- [x] **T-025** docs: ADR-0006 + README-секція
- [x] **T-026** субагенти `reverse-analyst` + `reviewer` (бандл `ai/agents/`) для нативного `/spec-forge analyze`

---
**ВСІ задачі (T-001…T-026 + фази) виконано.** Команди: `init · spec · plan · tasks · analyze · validate · deploy · status · export · command`.
`/spec-forge <підкоманда>` — диспетчер точних підкоманд (контент нативно на підписці, механічні через CLI). 47 тестів, ruff clean, coverage 91%.
