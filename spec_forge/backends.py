"""AI backends — a seam over the LLM (FR-010).

A single backend: `MockBackend` (deterministic, offline) — the default CLI scaffolding.
Real content is generated **natively in Claude Code** via role subagents (`/spec-forge`),
on the Claude subscription.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIBackend(ABC):
    @abstractmethod
    def draft(self, persona: str, context: str) -> str:
        """Returns an artifact draft on behalf of the persona."""


class MockBackend(AIBackend):
    """Deterministic backend for tests/offline."""

    def draft(self, persona: str, context: str) -> str:
        return f"<!-- draft by {persona} (mock backend) -->\n\n{context}\n"


def get_backend(name: str = "mock") -> AIBackend:
    if name == "mock":
        return MockBackend()
    raise ValueError(f"Unknown backend: {name}. Available: mock")
