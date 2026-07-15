# Git — usage (spec-forge)

A practical guide on how to work with this repository in git: from cloning to release,
taking the project's specifics into account (spec-bundle, symlinks, PDF review).

Repository: **https://github.com/chiperi/spec-forge**

---

## 1. Cloning and setup

```bash
git clone https://github.com/chiperi/spec-forge.git
cd spec-forge
uv sync                      # dependencies + locally installed spec-forge
uv run pytest                # make sure everything is green
```

> **macOS/Linux:** the repo has symlinks (`AGENTS.md`, `.claude/*`, dotfiles → `specifications/`).
> git restores them automatically. On **Windows**, enable symlink support:
> `git config --global core.symlinks true` (and Developer Mode), otherwise they arrive as text files.

Verify the committer identity once:
```bash
git config user.name   # Name
git config user.email  # email linked to GitHub
```

---

## 2. Branching model

- **`main`** — always green (CI passes). We do not push directly.
- **feature/fix branches** from `main`:
  ```bash
  git switch -c feat/openapi-lint        # new feature
  git switch -c fix/deploy-symlinks      # a fix
  git switch -c docs/git-guide           # documentation
  ```
- Merging into `main` — via Pull Request after green CI.

---

## 3. Commits (Conventional Commits)

Format: `<type>: <short description>` — `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
If there is a task id from the spec — add it: `feat: PDF export of the spec (T-019)`.

```bash
git add -A
git commit -m "feat: add export command (PDF snapshot, T-019)"
```

Keep commits small and atomic (one task = one commit, where possible).

---

## 4. Workflow with specification review (PDF)

A typical cycle when the team refines the specification:

```bash
git switch -c spec/review-round-1

# 1) generate/update artifacts (as needed)
#    real content — natively in Claude Code: /spec-forge spec · /spec-forge plan
#    the CLI below gives deterministic scaffolding (offline)
uv run spec-forge spec  .
uv run spec-forge plan  .
uv run spec-forge validate .

# 2) build a SINGLE PDF of all specification files for team review
uv run spec-forge export .
#   → exports/spec-forge-export-<timestamp>.pdf

# 3) open the PDF, have the team proofread it, mark which files need changes
# 4) make changes in the corresponding specifications/** files
# 5) commit
git add -A
git commit -m "docs: spec edits following review round-1"
git push -u origin spec/review-round-1
# → open a PR
```

> `exports/` is **in `.gitignore`** — PDFs are generated locally and not committed (binaries).
> If you want to share a specific snapshot — attach the PDF to a PR/issue manually.

---

## 5. Push and Pull Request

```bash
git push -u origin <your-branch>
```
Then on GitHub → **Compare & pull request**. CI (`.github/workflows/ci.yml`) will run
ruff + pytest + coverage on **ubuntu/macos/windows**. We merge only when CI is green.

Update your branch from main before merging:
```bash
git switch main && git pull
git switch <branch> && git rebase main   # or merge, per the team's convention
```

---

## 6. Specifics of this repo

| What | Detail |
|----|--------|
| **spec-bundle** | The whole specification is in `specifications/`; this is the source of truth, not a pile of root files. |
| **Deployed pointers** | The root files `AGENTS.md`, `.claude/*`, `.github/copilot-instructions.md`, dotfiles are **symlinks** into `specifications/` (created by `spec-forge deploy`). Committed as symlinks. |
| **`.gitattributes`** | This is a symlink → `specifications/platform/gitattributes`. git **does not read** rules from a symlinked `.gitattributes` (for security), so `eol=lf` normalization does not take effect for this repo. If you need it — replace the root `.gitattributes` with a real file. |
| **`.gitignore`** | Ignores `.venv/`, caches, `.coverage`, `.spec-forge/` (phase state), `exports/` (PDF), `.env`, `.DS_Store`. |
| **`uv.lock`** | Committed (dependency reproducibility). |
| **Font** | `spec_forge/assets/fonts/DejaVuSans.ttf` (free license) — needed for Cyrillic in PDF; committed. |

---

## 7. Release / tag

```bash
git switch main && git pull
git tag -a v0.1.0 -m "spec-forge 0.1.0"
git push origin v0.1.0
```

---

## 8. Cheat sheet

```bash
git status                      # what changed
git switch -c feat/x            # new branch
git add -A && git commit -m ".." # commit
git push -u origin feat/x       # push the branch
git switch main && git pull     # update main
git log --oneline -10           # history
uv run spec-forge export .      # PDF snapshot for review
```
