"""AI-бекенди — seam над LLM (FR-010).

Один бекенд: `MockBackend` (детермінований, офлайн) — CLI-скафолдинг за замовчуванням.
Реальний зміст генерується **нативно в Claude Code** через рольових субагентів (`/spec-forge`),
на підписці Claude.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIBackend(ABC):
    @abstractmethod
    def draft(self, persona: str, context: str) -> str:
        """Повертає чернетку артефакту від імені персони."""


class MockBackend(AIBackend):
    """Детермінований бекенд для тестів/офлайн."""

    def draft(self, persona: str, context: str) -> str:
        return f"<!-- draft by {persona} (mock backend) -->\n\n{context}\n"


def get_backend(name: str = "mock") -> AIBackend:
    if name == "mock":
        return MockBackend()
    raise ValueError(f"Невідомий backend: {name}. Доступний: mock")
