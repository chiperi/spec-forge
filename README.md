# spec-forge

**Stack-agnostic, spec-driven генератор документації.** Перетворює будь-який проєкт на повний,
**AI- та OS-friendly** бандл специфікацій (`specifications/`). Гібрид: **детермінований двигун**
(скафолдинг · lifecycle · валідація) + **AI-персони** (BA / SA / Designer / Developer), що наповнюють
змістом. Між кожною змістовою фазою — **людський gate**: ти вичитуєш артефакт і лише тоді йдеш далі.

> Цей README — практичний гайд: **ролі → функціонал → правила → повний цикл крок-за-кроком** на
> прикладі одного проєкту. Внутрішня будова тула описана у [`specifications/`](specifications/).

---

## 1. Ролі (персони)

Кожна фаза документа належить одній персоні. Персона — це і гайд для людини, і AI-субагент
(`specifications/ai/agents/*.md`). Головне в кожній — **межі**: чого роль **не** робить, щоб не «розповзатися».

| Персона | Коли активна | Володіє артефактом | Не робить |
|---|---|---|---|
| 👤 **Business Analyst** | старт фічі — ЩО/НАВІЩО | `product/specs/*/spec.md`, glossary | не обирає стек, не пише код |
| 🏛️ **Solution Architect** | після spec.md — ЯК | `architecture/plan.md`, ADR `decisions/`, `contracts/`, NFR, threat-model | не пише прод-код, не проєктує UI |
| 🎨 **Designer** | фічі з інтерфейсом | `design/` — flows, стани, дизайн-система, a11y | не визначає бекенд/БД, не пише код |
| 🛠️ **Developer** | після plan/tasks | `delivery/tasks.md`, далі `src/`+`tests/` | no scope creep, no silent refactors |
| 🔎 **code-reviewer** | після коду | рев'ю на баги/спрощення | — |
| ↩️ **reverse-analyst** | brownfield-аналіз | reverse-`spec.md` за наявним кодом | не вигадує відсутніх фіч |
| 📋 **reviewer** | brownfield-аналіз | `review.md` — gap/рев'ю-документ | не переписує код |

**Передавання по ланцюгу:**

```
BA (spec.md)  →  SA (plan.md + ADR + contracts)  →  Designer (design/)  ⤵
                                                     Developer (tasks.md → код)
```

---

## 2. Функціонал (команди = фази)

`spec-forge` — CLI із фазами життєвого циклу. Змістові фази виконує персона, механічні — детермінований двигун.

| Команда | Фаза | Хто виконує | Вхід → Вихід |
|---|---|---|---|
| `init` | скафолд | двигун (без AI) | тека → каркас `specifications/` під стек |
| `spec` | вимоги | 👤 BA | опис → `product/specs/001-feature/spec.md` |
| `plan` | архітектура | 🏛️ SA | `spec.md` → `architecture/plan.md` + ADR + контракти |
| `tasks` | план робіт | 🛠️ Developer | `plan.md` → `delivery/tasks.md` (атомарні задачі) |
| `validate` | quality gates | двигун (без AI) | бандл → pass/fail по гейтах |
| `deploy` | tool-discovery | двигун (без AI) | бандл → root-symlinks (`AGENTS.md`, `.claude/…`) |
| `export` | PDF-знімок | двигун (без AI) | бандл → `exports/spec-forge-export-<ts>.pdf` |
| `analyze` | brownfield | ↩️ reverse-analyst + 📋 reviewer | наявний код → `spec.md` + `review.md` |
| `status` | прогрес | двигун | стан → пройдені/наступна фаза |

Артефакти складаються в єдину теку `specifications/` (шари: `product/` · `architecture/` · `contracts/`
· `design/` · `delivery/` · `quality/` · `platform/` · `ai/` · `roles/` · `knowledge/`).

---

## 3. Встановлення (одноразово)

```bash
curl -fsSL https://raw.githubusercontent.com/chiperi/spec-forge/main/install.sh | bash
```

Ставить глобальний CLI **і** реєструє в Claude Code slash-команду `/spec-forge` + 7 рольових субагентів.
Прибрати все разом: `./uninstall.sh` (або `spec-forge command uninstall`). Перезавантаж Claude Code, щоб побачити `/spec-forge`.

---

## 4. Загальні правила використання

- **Порядок фаз фіксований:** `init → spec → plan → tasks → validate → deploy`. Кожна фаза читає артефакт попередньої.
- **Людський gate після кожної змістової фази** — вичитай і апрувни артефакт, перш ніж запускати наступну.
- **`[NEEDS CLARIFICATION]` блокує перехід.** Відкриті питання у `spec.md` не пускають далі, поки їх не закрито.
- **Ідемпотентність + re-spec.** Повторний запуск фази не дублює артефакти: показує **diff** і питає підтвердження перед перезаписом (ручні правки зберігаються). `--yes` / `-y` — пропустити підтвердження (для CI).
- **Два режими наповнення** (див. §6): нативний Claude Code (без API-ключа) або CLI `--backend claude`.
- **Stack-agnostic.** Стек задається профілем на `init` (`--stack python|node|go`) — ядро не змінюється.
- **Guardrails:** не комітай секрети/`.env`; не змінюй структуру бандла вручну; жодних «заодно» рефакторингів.

---

## 5. Повний цикл крок-за-кроком (приклад: `notes-api`)

Створимо документацію з нуля для одного проєкту — REST API для нотаток. Нижче обидва способи запуску:
🟢 **у Claude Code** (`/spec-forge …`, на підписці, без API-ключа) і ⚙️ **CLI** (`--backend claude`, потрібен `ANTHROPIC_API_KEY`).

### Крок 0 — тека проєкту
```bash
mkdir notes-api && cd notes-api
```

### Крок 1 — `init`: каркас `specifications/`
Детермінований скафолд під стек (AI не задіяний). Це механічна фаза — у Claude Code вона делегується тому ж локальному CLI.
```bash
⚙️  spec-forge init . --name "notes-api" --stack python   # флаги
    spec-forge init .                                      # або інтерактивне інтервʼю (назва, стек)
🟢  /spec-forge init                                       # той самий CLI з Claude Code
```
**Результат:** повна тека `specifications/` з усіма шарами + `.spec-forge/state.json`. → `status`: `✅ init`.

### Крок 2 — `spec` (👤 BA): вимоги
```bash
⚙️  spec-forge spec . -d "REST API для нотаток із тегами й повнотекстовим пошуком" --backend claude
🟢  /spec-forge spec REST API для нотаток із тегами й пошуком
```
**Результат:** `product/specs/001-feature/spec.md` — problem, user stories, acceptance (EARS / Given-When-Then), **вимірювані** success criteria (SC-…), glossary.
**🚦 Gate:** вичитай spec.md; закрий усі `[NEEDS CLARIFICATION]`.

### Крок 3 — `plan` (🏛️ SA): архітектура
```bash
⚙️  spec-forge plan . --backend claude
🟢  /spec-forge plan
```
**Вхід:** `spec.md`. **Результат:** `architecture/plan.md` + ADR (`decisions/`) + контракти (`openapi.yaml`) + NFR у числах + threat-model.
**🚦 Gate:** апрувни план і ключові рішення (ADR).

### Крок 4 — `design` (🎨 Designer) — *опційно, якщо є UI*
Для чистого API можна пропустити. Для інтерфейсу — user flows, стани компонентів, a11y (WCAG AA) у `design/`.

### Крок 5 — `tasks` (🛠️ Developer): план робіт
```bash
⚙️  spec-forge tasks . --backend claude
🟢  /spec-forge tasks
```
**Вхід:** `plan.md`. **Результат:** `delivery/tasks.md` — **атомарні, трасовані** задачі з чекбоксами: ID `T-001`, маркер `[P]` (паралельні), посилання на `US-/FR-/NFR-`.
**🚦 Gate:** переконайся, що задачі покривають усі вимоги.

### Крок 6 — `validate`: quality gates
```bash
spec-forge validate .            # однаково для обох режимів (без AI)
```
Проганяє 3 детермінованих гейти (падає з `exit 1`, якщо хоч один червоний):

| Gate | Перевіряє |
|---|---|
| `structure` | є `ai/AGENTS.md`, `architecture/plan.md`, ≥1 `spec.md` |
| `clarifications` | **0** відкритих `[NEEDS CLARIFICATION]` |
| `measurable-success` | у spec.md є `Success Criteria` з маркерами `SC-` |

### Крок 7 — `deploy`: розгортання для інструментів
```bash
spec-forge deploy .
```
Кладе в корінь **symlinks** на джерело правди в `specifications/` (`AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
`.claude/*`, dotfiles), щоб Claude/Cursor/Copilot знаходили конфіги за стандартними шляхами.

### Крок 8 — `export` (опційно): PDF для командного рев'ю
```bash
spec-forge export .              # → exports/spec-forge-export-<timestamp>.pdf
```

### Перевірка прогресу будь-коли
```bash
spec-forge status .
# ✅ init  ✅ spec  ✅ plan  ✅ tasks  ✅ validate  ✅ deploy  → усі фази пройдено
```

**Підсумок циклу:** `init → spec(BA) → plan(SA) → [design] → tasks(Dev) → validate → deploy` — спершу спека, потім архітектура, потім план робіт; людський gate між фазами.

---

## 6. Два режими наповнення

| | 🟢 Claude Code (нативно) | ⚙️ CLI |
|---|---|---|
| Виклик | `/spec-forge <підкоманда>` | `spec-forge <підкоманда> --backend claude` |
| Ключ | **не потрібен** (на підписці) | потрібен `ANTHROPIC_API_KEY` |
| Модель | субагенти в Claude Code | Anthropic Messages API, `claude-opus-4-8` |
| Механічні (`init`/`validate`/`export`/`deploy`/`status`) | делегуються локальному CLI | локальний CLI |

Дефолтний `--backend mock` — офлайн, детермінований (echo-скафолд без AI), зручний для тестів/CI.

---

## 7. Brownfield: документація з наявного коду

Якщо код уже є — відтвори спеку й отримай рев'ю, **не чіпаючи код**:
```bash
spec-forge analyze /path/to/project --backend claude
# → product/specs/002-existing/spec.md    (що робить сьогодні)
# → product/specs/002-existing/review.md   (що/де виправити, severity)
```

---

## Розробка тула (from source)

```bash
git clone https://github.com/chiperi/spec-forge.git && cd spec-forge
uv sync
uv run spec-forge --help
uv run ruff check . && uv run pytest --cov=spec_forge
```

Вимоги самого тула написані його ж spec-driven процесом (dogfooding) — див. [`specifications/`](specifications/).
