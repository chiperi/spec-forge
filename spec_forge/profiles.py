"""Stack-profiles — незалежність від стеку (seam, FR-007)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StackProfile:
    name: str
    runtime: str
    linter: str
    formatter: str
    test: str
    pin: str  # рядок для .tool-versions (mise/asdf)

    def render_context(self) -> dict[str, str]:
        return {
            "stack": self.name,
            "runtime": self.runtime,
            "linter": self.linter,
            "formatter": self.formatter,
            "test": self.test,
            "tool_versions": self.pin,
        }


PROFILES: dict[str, StackProfile] = {
    "python": StackProfile("python", "Python 3.12+", "ruff", "ruff format", "pytest", "python 3.12.0"),
    "node": StackProfile("node", "Node 20+", "biome", "biome format", "vitest", "nodejs 20.11.0"),
    "go": StackProfile("go", "Go 1.22+", "golangci-lint", "gofmt", "go test", "golang 1.22.0"),
}


def get_profile(name: str) -> StackProfile:
    try:
        return PROFILES[name]
    except KeyError:
        available = ", ".join(sorted(PROFILES))
        raise ValueError(f"Невідомий stack-profile: {name}. Доступні: {available}") from None
