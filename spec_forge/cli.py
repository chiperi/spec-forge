"""CLI (Typer) — flags + interactive prompts (FR-011)."""

from __future__ import annotations

import difflib
import os
from pathlib import Path

import typer

from . import codescan, integrations
from .backends import get_backend
from .deploy import deploy_root
from .export_pdf import export_bundle
from .models import InterviewAnswers
from .profiles import PROFILES, get_profile
from .scaffolder import BundleExistsError, scaffold
from .state import PHASES, load_state, mark_phase, phase_done
from .validators import validate_bundle

app = typer.Typer(
    help="spec-forge — a generator of high-quality specifications for any project.",
    no_args_is_help=True,
)


@app.callback()
def _main(ctx: typer.Context) -> None:
    """Auto-adds the Claude Code /spec-forge slash-command (opt-out: SPEC_FORGE_NO_SLASH=1)."""
    if ctx.invoked_subcommand in (None, "command"):
        return
    if os.environ.get("SPEC_FORGE_NO_SLASH"):
        return
    try:
        result = integrations.ensure_installed()
    except OSError:
        return
    if result.command_created or result.agents_created:
        n = len(result.agents_created)
        extra = f" + {n} subagents" if n else ""
        typer.secho(
            f"↪ Claude Code: /spec-forge{extra} ({result.command_path})",
            fg=typer.colors.BLUE,
        )


command_app = typer.Typer(
    help="Claude Code /spec-forge slash-command (add/remove).", no_args_is_help=True
)
app.add_typer(command_app, name="command")


# ---- helpers ----------------------------------------------------------------
def _require_bundle(path: Path) -> Path:
    bundle = path / "specifications"
    if not bundle.exists():
        typer.secho(
            "❌ No specifications/ — run `spec-forge init` first", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    return bundle


def _read_first_spec(bundle: Path) -> str | None:
    specs_dir = bundle / "product" / "specs"
    specs = sorted(specs_dir.rglob("spec.md")) if specs_dir.exists() else []
    return specs[0].read_text(encoding="utf-8") if specs else None


def _build_context(bundle: Path, description: str) -> str:
    parts: list[str] = []
    agents = bundle / "ai" / "AGENTS.md"
    if agents.exists():
        parts.append(
            "# Project context (AGENTS.md)\n" + agents.read_text(encoding="utf-8")
        )
    if description:
        parts.append("# Feature description\n" + description)
    if not parts:
        parts.append("No description — draft a basic starter specification.")
    parts.append("Write a complete product specification (spec.md) in Markdown.")
    return "\n\n".join(parts)


def _write_artifact(out: Path, new: str, *, updating: bool, yes: bool) -> bool:
    """Writes the artifact. If updating (re-spec, FR-012) and the file changes — diff + confirmation."""
    new = new if new.endswith("\n") else new + "\n"
    if updating and out.exists():
        old = out.read_text(encoding="utf-8")
        if old == new:
            typer.secho(f"= no changes: {out}", fg=typer.colors.YELLOW)
            return False
        if not yes:
            diff = "".join(
                difflib.unified_diff(
                    old.splitlines(keepends=True),
                    new.splitlines(keepends=True),
                    fromfile=f"{out} (current)",
                    tofile=f"{out} (new)",
                )
            )
            typer.echo(diff)
            if not typer.confirm(f"Overwrite {out}?"):
                typer.secho("↷ Cancelled — file not changed.", fg=typer.colors.YELLOW)
                return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new, encoding="utf-8")
    return True


def _build_code_context(
    code_ctx: str, bundle: Path, instruction: str, extra: str = ""
) -> str:
    parts = ["# Codebase\n" + code_ctx]
    agents = bundle / "ai" / "AGENTS.md"
    if agents.exists():
        parts.append(
            "# Project context (AGENTS.md)\n" + agents.read_text(encoding="utf-8")
        )
    if extra:
        parts.append(extra)
    parts.append(instruction)
    return "\n\n".join(parts)


def _draft(persona: str, context: str) -> str:
    return get_backend().draft(persona, context)


def _run_phase(
    path: Path,
    phase: str,
    persona: str,
    context: str,
    out_rel: str,
    yes: bool,
) -> None:
    bundle = path / "specifications"
    updating = phase_done(path, phase)
    draft = _draft(persona, context)
    out = bundle / out_rel
    written = _write_artifact(out, draft, updating=updating, yes=yes)
    if out.exists():
        mark_phase(path, phase)
    if written:
        label = "updated" if updating else "created"
        typer.secho(f"✅ {out_rel} {label}: {out}", fg=typer.colors.GREEN)


def _scaffold_notice() -> None:
    """CLI content commands only emit a deterministic mock placeholder — say so, loudly."""
    typer.secho(
        "ℹ mock scaffold placeholder — run the matching `/spec-forge` subcommand "
        "in Claude Code for real AI content.",
        fg=typer.colors.YELLOW,
    )


# ---- commands ---------------------------------------------------------------
@app.command()
def init(
    path: Path = typer.Argument(..., help="Project directory"),
    name: str = typer.Option(None, "--name", help="Project name"),
    stack: str = typer.Option(
        None, "--stack", help=f"Stack: {', '.join(sorted(PROFILES))}"
    ),
    summary: str = typer.Option("", "--summary", help="Short project description"),
    yes: bool = typer.Option(False, "--yes", "-y", help="No interactive questions"),
) -> None:
    """Scaffolds the specifications/ bundle into the project directory (US-1, FR-001/002/007)."""
    name = name or (
        path.name if yes else typer.prompt("Project name", default=path.name)
    )
    stack = stack or ("python" if yes else typer.prompt("Stack", default="python"))
    try:
        profile = get_profile(stack)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    answers = InterviewAnswers(project_name=name, stack=stack, summary=summary)
    ctx = {
        "project": answers.project_name,
        "summary": answers.summary,
        **profile.render_context(),
    }

    try:
        written = scaffold(path, ctx)
    except BundleExistsError as exc:
        typer.secho(
            f"❌ {exc} (to update artifacts, use the spec/plan/tasks phases)",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from exc

    mark_phase(path, "init")
    typer.secho(
        f"✅ specifications/ created in {path} ({len(written)} files, stack: {stack})",
        fg=typer.colors.GREEN,
    )


@app.command()
def spec(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    description: str = typer.Option(
        "", "--description", "-d", help="Project/feature description"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Overwrite without confirmation"
    ),
) -> None:
    """(BA) Draft spec.md requirements — scaffold placeholder; real content via /spec-forge spec (US-2, FR-003)."""
    bundle = _require_bundle(path)
    context = _build_context(bundle, description)
    _run_phase(
        path,
        "spec",
        "business-analyst",
        context,
        "product/specs/001-feature/spec.md",
        yes,
    )
    _scaffold_notice()


@app.command()
def plan(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Overwrite without confirmation"
    ),
) -> None:
    """(SA) Technical plan plan.md — scaffold placeholder; real content via /spec-forge plan (US-3, FR-004)."""
    bundle = _require_bundle(path)
    spec_text = _read_first_spec(bundle)
    if spec_text is None:
        typer.secho("❌ No spec.md — run `spec-forge spec` first", fg=typer.colors.RED)
        raise typer.Exit(1)
    context = (
        "# Requirements (spec.md)\n"
        + spec_text
        + "\n\nWrite a technical plan (plan.md) in Markdown."
    )
    _run_phase(path, "plan", "solution-architect", context, "architecture/plan.md", yes)
    _scaffold_notice()


@app.command()
def tasks(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Overwrite without confirmation"
    ),
) -> None:
    """Derive delivery/tasks.md tasks — scaffold placeholder; real content via /spec-forge tasks (US-4, FR-005)."""
    bundle = _require_bundle(path)
    plan_file = bundle / "architecture" / "plan.md"
    if not plan_file.exists():
        typer.secho("❌ No plan.md — run `spec-forge plan` first", fg=typer.colors.RED)
        raise typer.Exit(1)
    context = (
        "# Technical plan (plan.md)\n"
        + plan_file.read_text(encoding="utf-8")
        + "\n\nDerive atomic, traceable tasks (tasks.md) in Markdown with checkboxes."
    )
    _run_phase(path, "tasks", "developer", context, "delivery/tasks.md", yes)
    _scaffold_notice()


@app.command()
def design(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Overwrite without confirmation"
    ),
) -> None:
    """(Designer, optional) UX/UI design spec — scaffold placeholder; real content via /spec-forge design."""
    bundle = _require_bundle(path)
    spec_text = _read_first_spec(bundle)
    if spec_text is None:
        typer.secho("❌ No spec.md — run `spec-forge spec` first", fg=typer.colors.RED)
        raise typer.Exit(1)
    context = (
        "# Requirements (spec.md)\n"
        + spec_text
        + "\n\nWrite the UX/UI design spec (user flows, component states, a11y) in Markdown."
    )
    _run_phase(path, "design", "designer", context, "design/feature.design.md", yes)
    _scaffold_notice()


@app.command()
def validate(path: Path = typer.Argument(Path("."), help="Project directory")) -> None:
    """Run the quality gates over the bundle (US-5, FR-006)."""
    bundle = _require_bundle(path)
    results = validate_bundle(bundle)
    for r in results:
        icon = "✅" if r.passed else "❌"
        color = typer.colors.GREEN if r.passed else typer.colors.RED
        typer.secho(f"{icon} {r.gate}", fg=color)
        for gap in r.gaps:
            typer.secho(f"   - {gap}", fg=typer.colors.YELLOW)
    if any(not r.passed for r in results):
        raise typer.Exit(1)
    mark_phase(path, "validate")
    typer.secho("All gates are green.", fg=typer.colors.GREEN)


@app.command()
def deploy(path: Path = typer.Argument(Path("."), help="Project directory")) -> None:
    """Root symlinks for tool-discovery (US-6, FR-008)."""
    _require_bundle(path)
    created = deploy_root(path)
    mark_phase(path, "deploy")
    typer.secho(
        f"✅ Deployed {len(created)} pointers: {', '.join(created)}",
        fg=typer.colors.GREEN,
    )


@app.command()
def export(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    out: str = typer.Option("exports", "--out", help="Directory for the PDF"),
) -> None:
    """Export all specifications/ files into a single timestamped PDF (FR-013)."""
    _require_bundle(path)
    pdf = export_bundle(path, out)
    typer.secho(f"✅ PDF snapshot: {pdf}", fg=typer.colors.GREEN)


@app.command()
def analyze(
    source: Path = typer.Argument(
        ..., help="Directory of an EXISTING project for code analysis"
    ),
    path: Path = typer.Option(
        None, "--path", help="Where to write specifications/ (default = source)"
    ),
    slug: str = typer.Option(
        "002-existing", "--slug", help="Folder under product/specs/"
    ),
    only: str = typer.Option("both", "--only", help="both | spec | review"),
    max_file_bytes: int = typer.Option(
        100_000, "--max-file-bytes", help="Per-file limit (bytes)"
    ),
    max_chars: int = typer.Option(
        200_000, "--max-chars", help="Context limit (characters)"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Overwrite without confirmation"
    ),
) -> None:
    """(Reverse) Spec + review of EXISTING code (brownfield) — deterministic scaffolding.

    Real content comes natively via `/spec-forge analyze` in Claude Code (subagents).
    """
    if only not in ("both", "spec", "review"):
        raise typer.BadParameter("--only must be: both | spec | review")
    if not source.is_dir():
        typer.secho(f"❌ No directory: {source}", fg=typer.colors.RED)
        raise typer.Exit(1)

    target = path or source
    bundle = target / "specifications"
    try:
        code_ctx = codescan.scan_codebase(
            source, max_file_bytes=max_file_bytes, max_total_chars=max_chars
        )
    except OSError as exc:
        typer.secho(f"❌ Code scan: {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    if only in ("both", "spec"):
        ctx = _build_code_context(
            code_ctx,
            bundle,
            "Derive the ACTUAL product specification (spec.md) from this code, with references to files.",
        )
        _run_phase(
            target,
            "analyze",
            "reverse-analyst",
            ctx,
            f"product/specs/{slug}/spec.md",
            yes,
        )

    if only in ("both", "review"):
        inferred = bundle / "product" / "specs" / slug / "spec.md"
        docs: list[str] = []
        if inferred.exists():
            docs.append(
                "# Inferred spec (spec.md)\n" + inferred.read_text(encoding="utf-8")
            )
        expected = _read_first_spec(bundle)
        if expected and (
            not inferred.exists() or expected != inferred.read_text(encoding="utf-8")
        ):
            docs.append("# Expected spec (existing)\n" + expected)
        for rel in ("architecture/plan.md", "delivery/tasks.md"):
            doc = bundle / rel
            if doc.exists():
                docs.append(
                    f"# Existing doc ({rel})\n" + doc.read_text(encoding="utf-8")
                )
        ctx = _build_code_context(
            code_ctx,
            bundle,
            "Reconcile the DOCS (specifications/) against the code. Compose a review/gap document: what is "
            "missing in the docs, deficiencies and DRIFT (code changed, docs didn't); WHERE to fix (doc file + "
            "section), severity; for each discrepancy — a concrete doc-rewrite option; a verdict on whether the "
            "docs match the code. Don't touch the code, only propose doc rewrites.",
            extra="\n\n".join(docs),
        )
        _run_phase(
            target, "review", "reviewer", ctx, f"product/specs/{slug}/review.md", yes
        )
    _scaffold_notice()


@app.command()
def status(path: Path = typer.Argument(Path("."), help="Project directory")) -> None:
    """Show lifecycle progress (FR-009)."""
    done = set(load_state(path).get("phases", []))
    for ph in PHASES:
        icon = "✅" if ph in done else "⬜"
        typer.secho(f"{icon} {ph}")
    nxt = next((p for p in PHASES if p not in done), None)
    if nxt:
        typer.secho(f"→ next phase: {nxt}", fg=typer.colors.BLUE)
    else:
        typer.secho("All phases complete.", fg=typer.colors.GREEN)


@command_app.command("install")
def command_install(
    project: bool = typer.Option(
        False, "--project", help="Into the current project instead of globally"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite the command and subagents"
    ),
) -> None:
    """Add the /spec-forge slash-command + role subagents (globally or into the project)."""
    root = Path(".") if project else None
    result = integrations.ensure_installed(root, force=force)
    typer.secho(f"✅ /spec-forge: {result.command_path}", fg=typer.colors.GREEN)
    typer.secho(
        f"   subagents written: {len(result.agents_created)}", fg=typer.colors.GREEN
    )


@command_app.command("uninstall")
def command_uninstall(
    project: bool = typer.Option(
        False, "--project", help="From the current project instead of globally"
    ),
) -> None:
    """Remove the /spec-forge slash-command + role subagents."""
    root = Path(".") if project else None
    result = integrations.remove(root)
    if result.command_removed or result.agents_removed:
        typer.secho(
            f"✅ removed: command + {len(result.agents_removed)} subagents",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho("= nothing was there", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()
