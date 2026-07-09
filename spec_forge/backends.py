"""AI-бекенди — seam над LLM (FR-010).

MVP: MockBackend (детермінований, офлайн) + ClaudeBackend (реальний, Anthropic Messages API).
Драфтинг спеки — це single-shot генерація тексту, тож правильна поверхня — Messages API
(одна відповідь), а не важчий Agent SDK / Managed Agents. Рішення зафіксовано в ADR-0002.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

DEFAULT_MODEL = "claude-opus-4-8"

# Системні промпти персон (межі — з roles/; повний контекст у specifications/roles/).
_PERSONA_DEFAULT = (
    "Ти досвідчений інженер. Дай чіткий, структурований результат у Markdown."
)
PERSONA_SYSTEM: dict[str, str] = {
    "business-analyst": (
        "Ти Business Analyst. Перетвори вхідний контекст на чітку, тестовану "
        "специфікацію вимог (spec.md) у Markdown.\n"
        "- Вимоги у EARS («WHEN … THE SYSTEM SHALL …») або Given/When/Then.\n"
        "- User stories незалежно тестовані; P1 = самодостатній MVP.\n"
        "- Success criteria вимірювані й технологічно-незалежні.\n"
        "- Веди glossary; двозначності познач [NEEDS CLARIFICATION].\n"
        "Межі: НЕ обирай стек/архітектуру, НЕ пиши код. Виведи ЛИШЕ Markdown спеки."
    ),
    "solution-architect": (
        "Ти Solution Architect. За вимогами склади технічний план (plan.md) у Markdown: "
        "стиль архітектури (обґрунтуй), стек, компоненти, модель даних, контракти, "
        "NFR у числах, ключові рішення (ADR-стиль), тестова стратегія.\n"
        "Межі: НЕ пиши продакшн-код; розбіжності у вимогах познач [NEEDS CLARIFICATION]."
    ),
    "designer": (
        "Ти Designer (UX/UI). За вимогами опиши досвід у Markdown: user flows, стани "
        "компонентів (default/hover/focus/disabled/loading/error/empty), responsive, "
        "дизайн-систему/токени, a11y-критерії (WCAG AA як acceptance).\n"
        "Межі: НЕ визначай бекенд/модель даних; НЕ пиши продакшн-код."
    ),
    "developer": (
        "Ти Developer. За планом і задачами опиши реалізацію у Markdown: кроки, ключові "
        "модулі/функції, тести за acceptance-сценаріями. Дотримуйся контрактів і конвенцій.\n"
        "Межі: no scope creep; no silent refactors; не міняй архітектуру/вимоги мовчки."
    ),
    "reverse-analyst": (
        "Ти Reverse-Engineering Analyst. За наданим деревом файлів і кодом виведи ФАКТИЧНУ "
        "специфікацію проєкту (spec.md) у Markdown: що він робить сьогодні, точки входу, "
        "поведінка у форматі EARS / Given-When-Then, модель даних, зовнішні залежності, інваріанти.\n"
        "- Для кожного твердження ПОСИЛАЙСЯ на шлях файлу.\n"
        "- Здогади/двозначності познач `[NEEDS CLARIFICATION]`.\n"
        "Межі: НЕ вигадуй відсутніх у коді фіч; НЕ пропонуй змін (це робота рев'ю). Лише Markdown."
    ),
    "reviewer": (
        "Ти Reviewer / Gap-аналітик. Порівняй код (і виведену спеку, і будь-які очікування) з "
        "best practices. Склади рев'ю-документ у Markdown:\n"
        "- таблиця Implemented / Missing / Incorrect;\n"
        "- ДЕ виправити (файл + секція) і severity;\n"
        "- correctness / security / test-coverage занепокоєння;\n"
        "- явний вердикт, чи «написано як треба».\n"
        "Посилайся на шляхи файлів; будь конкретним і дієвим.\n"
        "Межі: НЕ переписуй код. Лише Markdown."
    ),
}


class AIBackend(ABC):
    @abstractmethod
    def draft(self, persona: str, context: str) -> str:
        """Повертає чернетку артефакту від імені персони."""


class MockBackend(AIBackend):
    """Детермінований бекенд для тестів/офлайн."""

    def draft(self, persona: str, context: str) -> str:
        return f"<!-- draft by {persona} (mock backend) -->\n\n{context}\n"


class ClaudeBackend(AIBackend):
    """Реальний бекенд через Anthropic Messages API (single-shot драфтинг)."""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model

    def draft(self, persona: str, context: str) -> str:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - залежить від оточення
            raise RuntimeError(
                "Пакет 'anthropic' не встановлено. Додай: uv add anthropic"
            ) from exc

        client = anthropic.Anthropic()  # креденшли з ANTHROPIC_API_KEY або ant-профілю
        system = PERSONA_SYSTEM.get(persona, _PERSONA_DEFAULT)
        with client.messages.stream(
            model=self.model,
            max_tokens=16000,
            system=system,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": context}],
        ) as stream:
            message = stream.get_final_message()

        return "".join(b.text for b in message.content if b.type == "text").strip()


def get_backend(name: str, model: str | None = None) -> AIBackend:
    if name == "mock":
        return MockBackend()
    if name == "claude":
        return ClaudeBackend(model or DEFAULT_MODEL)
    available = "mock, claude"
    raise ValueError(f"Невідомий backend: {name}. Доступні: {available}")
