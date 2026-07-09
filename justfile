# spec-forge — lifecycle & dev tasks (потрібен `just`: https://github.com/casey/just)

# Встановити глобально + зареєструвати /spec-forge (CLI і slash разом)
install:
    ./install.sh

# Прибрати /spec-forge + видалити тул (разом)
uninstall:
    ./uninstall.sh

# Синхронізувати залежності (dev)
sync:
    uv sync

# Лінт
lint:
    uv run ruff check .

# Тести + покриття
test:
    uv run pytest --cov=spec_forge --cov-fail-under=85
