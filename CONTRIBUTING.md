# Contributing

Thanks for your interest in spec-forge. This is a small personal project, but issues and pull requests are welcome.

## Setup

```bash
git clone https://github.com/chiperi/spec-forge.git
cd spec-forge
uv sync
uv run spec-forge --help
```

## Workflow

- **Spec-first.** This tool's own requirements live in [`specifications/`](specifications/) (dogfooding). For a non-trivial change, update the relevant spec/plan/tasks alongside the code.
- **Docs in English** by default (project convention).
- Keep changes focused — no large "drive-by" refactors.

## Quality gates (run before opening a PR)

```bash
uv run ruff check .      # lint
uv run ruff format .     # format
uv run pytest            # tests
```

CI (`.github/workflows/ci.yml`) runs ruff + pytest with coverage ≥ 85% on Ubuntu, macOS and Windows. A PR merges only when it is green.

## Pull requests

- `main` is protected — **branch off `main` and open a PR**; direct pushes are blocked.
- Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `chore:`, `test:`. Reference a task id when relevant, e.g. `feat: add export command (T-019)`.
- Keep commits small and atomic.

## Security

Please do not open public issues for security problems — see [SECURITY.md](SECURITY.md). And never commit secrets or a real `.env`.
