# Git — використання (spec-forge)

Практична інструкція, як працювати з цим репозиторієм у git: від клонування до релізу,
з урахуванням особливостей проєкту (spec-bundle, symlinks, PDF-рев'ю).

Репозиторій: **https://github.com/chiperi/spec-forge**

---

## 1. Клонування й налаштування

```bash
git clone https://github.com/chiperi/spec-forge.git
cd spec-forge
uv sync                      # залежності + локально встановлений spec-forge
uv run pytest                # переконатися, що все зелене
```

> **macOS/Linux:** у репо є symlinks (`AGENTS.md`, `.claude/*`, dotfiles → `specifications/`).
> git відновлює їх автоматично. На **Windows** увімкни підтримку symlinks:
> `git config --global core.symlinks true` (і Developer Mode), інакше вони приїдуть як текстові файли.

Одноразово перевір ідентичність коміттера:
```bash
git config user.name   # Ім'я
git config user.email  # пошта, звʼязана з GitHub
```

---

## 2. Модель гілок

- **`main`** — завжди зелена (CI проходить). Напряму не пушимо.
- **feature/fix-гілки** від `main`:
  ```bash
  git switch -c feat/openapi-lint        # нова фіча
  git switch -c fix/deploy-symlinks      # виправлення
  git switch -c docs/git-guide           # документація
  ```
- Мердж у `main` — через Pull Request після зеленого CI.

---

## 3. Коміти (Conventional Commits)

Формат: `<type>: <короткий опис>` — `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
Якщо є id задачі зі спеки — додай його: `feat: PDF-експорт спеки (T-019)`.

```bash
git add -A
git commit -m "feat: додати команду export (PDF-знімок, T-019)"
```

Тримай коміти маленькими й атомарними (одна задача = один коміт, де можливо).

---

## 4. Робочий цикл з рев'ю специфікації (PDF)

Типовий цикл, коли команда доопрацьовує специфікацію:

```bash
git switch -c spec/review-round-1

# 1) згенерувати/оновити артефакти (за потреби)
uv run spec-forge spec  . --backend claude
uv run spec-forge plan  . --backend claude
uv run spec-forge validate .

# 2) зібрати ЄДИНИЙ PDF усіх файлів специфікації для командного рев'ю
uv run spec-forge export .
#   → exports/spec-forge-export-<timestamp>.pdf

# 3) відкрити PDF, командою вичитати, позначити, у яких файлах треба зміни
# 4) внести зміни у відповідні файли specifications/**
# 5) закомітити
git add -A
git commit -m "docs: правки спеки за підсумком рев'ю round-1"
git push -u origin spec/review-round-1
# → відкрити PR
```

> `exports/` **у `.gitignore`** — PDF-и генеруються локально й не комітяться (бінарники).
> Хочеш поділитися конкретним знімком — прикріпи PDF у PR/issue вручну.

---

## 5. Push і Pull Request

```bash
git push -u origin <твоя-гілка>
```
Далі на GitHub → **Compare & pull request**. CI (`.github/workflows/ci.yml`) прожене
ruff + pytest + coverage на **ubuntu/macos/windows**. Мерджимо лише коли CI зелений.

Оновити гілку від main перед мерджем:
```bash
git switch main && git pull
git switch <гілка> && git rebase main   # або merge, за домовленістю команди
```

---

## 6. Особливості цього репо

| Що | Деталь |
|----|--------|
| **spec-bundle** | Уся специфікація — у `specifications/`; це джерело правди, а не купа root-файлів. |
| **Deployed pointers** | root-файли `AGENTS.md`, `.claude/*`, `.github/copilot-instructions.md`, dotfiles — це **symlinks** у `specifications/` (створює `spec-forge deploy`). Комітяться як symlinks. |
| **`.gitattributes`** | Це symlink → `specifications/platform/gitattributes`. git **не читає** правила з symlink-нутого `.gitattributes` (безпека), тож `eol=lf`-нормалізація для цього репо не діє. Якщо треба — заміни root `.gitattributes` на реальний файл. |
| **`.gitignore`** | Ігнорує `.venv/`, кеші, `.coverage`, `.spec-forge/` (стан фаз), `exports/` (PDF), `.env`, `.DS_Store`. |
| **`uv.lock`** | Комітиться (відтворюваність залежностей). |
| **Шрифт** | `spec_forge/assets/fonts/DejaVuSans.ttf` (вільна ліцензія) — потрібен для кирилиці в PDF; комітиться. |

---

## 7. Реліз / тег

```bash
git switch main && git pull
git tag -a v0.1.0 -m "spec-forge 0.1.0"
git push origin v0.1.0
```

---

## 8. Шпаргалка

```bash
git status                      # що змінено
git switch -c feat/x            # нова гілка
git add -A && git commit -m ".." # закомітити
git push -u origin feat/x       # запушити гілку
git switch main && git pull     # оновити main
git log --oneline -10           # історія
uv run spec-forge export .      # PDF-знімок для рев'ю
```
