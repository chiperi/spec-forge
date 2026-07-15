"""Quality gates on the specification bundle (FR-006).

Deterministic checks (no AI): structural completeness, absence of open
[NEEDS CLARIFICATION], presence of measurable success criteria.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CLARIFICATION_MARKER = "[NEEDS CLARIFICATION"

# A genuine open marker sits in prose. Mentions of the marker as a *term* are written
# as inline code (`[NEEDS CLARIFICATION]`) or inside a code-fence — those are not counted,
# otherwise a spec that describes the marker itself would falsely fail its own gate.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")


def _strip_code(text: str) -> str:
    """Strips code-fences and inline code → only "prose" markers remain."""
    return _INLINE_CODE_RE.sub(" ", _CODE_FENCE_RE.sub(" ", text))

# Files that `init` + phases must guarantee (the tool's minimal bundle).
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
    gaps = [f"missing {p}" for p in REQUIRED_FILES if not (bundle / p).exists()]
    if not _spec_files(bundle):
        gaps.append("missing product/specs/**/spec.md")
    return ValidationResult("structure", not gaps, gaps)


def check_clarifications(bundle: Path) -> ValidationResult:
    gaps: list[str] = []
    for f in _spec_files(bundle):
        n = _strip_code(f.read_text(encoding="utf-8")).count(CLARIFICATION_MARKER)
        if n:
            gaps.append(f"{f.relative_to(bundle)}: {n} unresolved [NEEDS CLARIFICATION]")
    return ValidationResult("clarifications", not gaps, gaps)


def check_measurable(bundle: Path) -> ValidationResult:
    gaps: list[str] = []
    for f in _spec_files(bundle):
        text = f.read_text(encoding="utf-8")
        if "Success Criteria" not in text or "SC-" not in text:
            gaps.append(f"{f.relative_to(bundle)}: no measurable Success Criteria (SC-…)")
    return ValidationResult("measurable-success", not gaps, gaps)


def validate_bundle(bundle: Path) -> list[ValidationResult]:
    return [
        check_structure(bundle),
        check_clarifications(bundle),
        check_measurable(bundle),
    ]
