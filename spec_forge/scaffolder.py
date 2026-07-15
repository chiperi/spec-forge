"""Deterministic scaffolder for the specifications/ bundle (FR-001)."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATES_DIR = Path(__file__).parent / "templates" / "bundle"


class BundleExistsError(Exception):
    """specifications/ already exists (to update it, use re-spec mode, US-8)."""


def _iter_templates(root: Path) -> list[Path]:
    # Deterministic, sorted traversal → byte-for-byte identity (NFR-002/003).
    return sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix())


def scaffold(target: Path, context: dict) -> list[str]:
    """Renders the built-in template into <target>/specifications/. Returns the list of files."""
    bundle = target / "specifications"
    if bundle.exists():
        raise BundleExistsError(f"{bundle} already exists")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )

    written: list[str] = []
    for tpl in _iter_templates(TEMPLATES_DIR):
        rel = tpl.relative_to(TEMPLATES_DIR)
        if tpl.suffix == ".j2":
            content = env.get_template(rel.as_posix()).render(**context)
            out_rel = rel.with_suffix("")  # strip .j2
        else:
            content = tpl.read_text(encoding="utf-8")
            out_rel = rel
        out = bundle / out_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        written.append(out_rel.as_posix())

    # ai aliases as symlinks to the single source (AGENTS.md)
    ai_agents = bundle / "ai" / "AGENTS.md"
    if ai_agents.exists():
        for alias in ("CLAUDE.md", "GEMINI.md"):
            link = bundle / "ai" / alias
            if not link.exists() and not link.is_symlink():
                link.symlink_to("AGENTS.md")
                written.append((link.relative_to(bundle)).as_posix())

    return sorted(written)
