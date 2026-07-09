"""Quality gates на bundle специфікації (FR-006).

Детерміновані перевірки (без AI): структурна повнота, відсутність відкритих
[NEEDS CLARIFICATION], наявність вимірюваних success criteria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

CLARIFICATION_MARKER = "[NEEDS CLARIFICATION"

# Файли, які має гарантувати `init` + фази (мінімальний bundle тула).
REQUIRED_FILES = ["ai/AGENTS.md", "architecture/plan.md"]


@dataclass
class ValidationResult:
    gate: str
    passed: bool
    gaps: list[str] = field(default_factory=list)


def _spec_files(bundle: Path) -> list[Path]:
    specs_dir = bundle / "product" / "specs"
    return sorted(specs_dir.rglob("spec.md")) if specs_dir.exists() else []


def check_structure(bundle: Path) -> ValidationResult:
    gaps = [f"відсутній {p}" for p in REQUIRED_FILES if not (bundle / p).exists()]
    if not _spec_files(bundle):
        gaps.append("відсутній product/specs/**/spec.md")
    return ValidationResult("structure", not gaps, gaps)


def check_clarifications(bundle: Path) -> ValidationResult:
    gaps: list[str] = []
    for f in _spec_files(bundle):
        n = f.read_text(encoding="utf-8").count(CLARIFICATION_MARKER)
        if n:
            gaps.append(f"{f.relative_to(bundle)}: {n} незакритих [NEEDS CLARIFICATION]")
    return ValidationResult("clarifications", not gaps, gaps)


def check_measurable(bundle: Path) -> ValidationResult:
    gaps: list[str] = []
    for f in _spec_files(bundle):
        text = f.read_text(encoding="utf-8")
        if "Success Criteria" not in text or "SC-" not in text:
            gaps.append(f"{f.relative_to(bundle)}: немає вимірюваних Success Criteria (SC-…)")
    return ValidationResult("measurable-success", not gaps, gaps)


def validate_bundle(bundle: Path) -> list[ValidationResult]:
    return [
        check_structure(bundle),
        check_clarifications(bundle),
        check_measurable(bundle),
    ]
