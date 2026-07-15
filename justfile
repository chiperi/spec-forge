# spec-forge — lifecycle & dev tasks (requires `just`: https://github.com/casey/just)

# Install globally + register /spec-forge (CLI and slash together)
install:
    ./install.sh

# Remove /spec-forge + uninstall the tool (together)
uninstall:
    ./uninstall.sh

# Sync dependencies (dev)
sync:
    uv sync

# Lint
lint:
    uv run ruff check .

# Tests + coverage
test:
    uv run pytest --cov=spec_forge --cov-fail-under=85
