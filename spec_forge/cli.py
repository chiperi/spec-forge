"""CLI (Typer) — флаги + інтерактивні prompt-и (FR-011)."""

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
    help="spec-forge — генератор якісних специфікацій для будь-якого проєкту.",
    no_args_is_help=True,
)


@app.callback()
def _main(ctx: typer.Context) -> None:
    """Автододавання slash-команди Claude Code /spec-forge (opt-out: SPEC_FORGE_NO_SLASH=1)."""
    if ctx.invoked_subcommand in (None, "command"):
        return
    if os.environ.get("SPEC_FORGE_NO_SLASH"):
        return
    try:
        path, created = integrations.ensure_installed()
    except OSError:
        return
    if created:
        typer.secho(
            f"↪ додано slash-команду Claude Code: /spec-forge ({path})", fg=typer.colors.BLUE
        )


command_app = typer.Typer(help="Slash-команда Claude Code /spec-forge (add/remove).", no_args_is_help=True)
app.add_typer(command_app, name="command")


# ---- helpers ----------------------------------------------------------------
def _require_bundle(path: Path) -> Path:
    bundle = path / "specifications"
    if not bundle.exists():
        typer.secho("❌ Немає specifications/ — спершу `spec-forge init`", fg=typer.colors.RED)
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
        parts.append("# Project context (AGENTS.md)\n" + agents.read_text(encoding="utf-8"))
    if description:
        parts.append("# Feature description\n" + description)
    if not parts:
        parts.append("Немає опису — склади базову стартову специфікацію.")
    parts.append("Напиши повну специфікацію продукту (spec.md) у Markdown.")
    return "\n\n".join(parts)


def _write_artifact(out: Path, new: str, *, updating: bool, yes: bool) -> bool:
    """Пише артефакт. Якщо updating (re-spec, FR-012) і файл змінюється — diff + підтвердження."""
    new = new if new.endswith("\n") else new + "\n"
    if updating and out.exists():
        old = out.read_text(encoding="utf-8")
        if old == new:
            typer.secho(f"= без змін: {out}", fg=typer.colors.YELLOW)
            return False
        if not yes:
            diff = "".join(
                difflib.unified_diff(
                    old.splitlines(keepends=True),
                    new.splitlines(keepends=True),
                    fromfile=f"{out} (поточний)",
                    tofile=f"{out} (новий)",
                )
            )
            typer.echo(diff)
            if not typer.confirm(f"Перезаписати {out}?"):
                typer.secho("↷ Скасовано — файл не змінено.", fg=typer.colors.YELLOW)
                return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new, encoding="utf-8")
    return True


def _build_code_context(code_ctx: str, bundle: Path, instruction: str, extra: str = "") -> str:
    parts = ["# Codebase\n" + code_ctx]
    agents = bundle / "ai" / "AGENTS.md"
    if agents.exists():
        parts.append("# Project context (AGENTS.md)\n" + agents.read_text(encoding="utf-8"))
    if extra:
        parts.append(extra)
    parts.append(instruction)
    return "\n\n".join(parts)


def _draft(bundle: Path, persona: str, context: str, backend: str, model: str | None) -> str:
    try:
        return get_backend(backend, model).draft(persona, context)
    except Exception as exc:
        typer.secho(f"❌ {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc


def _run_phase(
    path: Path,
    phase: str,
    persona: str,
    context: str,
    out_rel: str,
    backend: str,
    model: str | None,
    yes: bool,
) -> None:
    bundle = path / "specifications"
    updating = phase_done(path, phase)
    draft = _draft(bundle, persona, context, backend, model)
    out = bundle / out_rel
    written = _write_artifact(out, draft, updating=updating, yes=yes)
    if out.exists():
        mark_phase(path, phase)
    if written:
        label = "оновлено" if updating else "створено"
        typer.secho(f"✅ {out_rel} {label}: {out}", fg=typer.colors.GREEN)


# ---- commands ---------------------------------------------------------------
@app.command()
def init(
    path: Path = typer.Argument(..., help="Тека проєкту"),
    name: str = typer.Option(None, "--name", help="Назва проєкту"),
    stack: str = typer.Option(None, "--stack", help=f"Стек: {', '.join(sorted(PROFILES))}"),
    summary: str = typer.Option("", "--summary", help="Короткий опис проєкту"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Без інтерактивних питань"),
) -> None:
    """Скафолдить bundle specifications/ у теку проєкту (US-1, FR-001/002/007)."""
    name = name or (path.name if yes else typer.prompt("Назва проєкту", default=path.name))
    stack = stack or ("python" if yes else typer.prompt("Стек", default="python"))
    try:
        profile = get_profile(stack)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    answers = InterviewAnswers(project_name=name, stack=stack, summary=summary)
    ctx = {"project": answers.project_name, "summary": answers.summary, **profile.render_context()}

    try:
        written = scaffold(path, ctx)
    except BundleExistsError as exc:
        typer.secho(f"❌ {exc} (для оновлення артефактів — фази spec/plan/tasks)", fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    mark_phase(path, "init")
    typer.secho(
        f"✅ specifications/ створено у {path} ({len(written)} файлів, стек: {stack})",
        fg=typer.colors.GREEN,
    )


@app.command()
def spec(
    path: Path = typer.Argument(Path("."), help="Тека проєкту"),
    description: str = typer.Option("", "--description", "-d", help="Опис проєкту/фічі"),
    backend: str = typer.Option("mock", "--backend", help="AI-бекенд: mock | claude"),
    model: str = typer.Option(None, "--model", help="Модель для claude-бекенду"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Перезаписати без підтвердження"),
) -> None:
    """(BA) Чернетка вимог spec.md через персону (US-2, FR-003)."""
    bundle = _require_bundle(path)
    context = _build_context(bundle, description)
    _run_phase(
        path, "spec", "business-analyst", context,
        "product/specs/001-feature/spec.md", backend, model, yes,
    )


@app.command()
def plan(
    path: Path = typer.Argument(Path("."), help="Тека проєкту"),
    backend: str = typer.Option("mock", "--backend", help="AI-бекенд: mock | claude"),
    model: str = typer.Option(None, "--model", help="Модель для claude-бекенду"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Перезаписати без підтвердження"),
) -> None:
    """(SA) Технічний план plan.md за spec.md (US-3, FR-004)."""
    bundle = _require_bundle(path)
    spec_text = _read_first_spec(bundle)
    if spec_text is None:
        typer.secho("❌ Немає spec.md — спершу `spec-forge spec`", fg=typer.colors.RED)
        raise typer.Exit(1)
    context = (
        "# Requirements (spec.md)\n" + spec_text + "\n\nНапиши технічний план (plan.md) у Markdown."
    )
    _run_phase(path, "plan", "solution-architect", context, "architecture/plan.md", backend, model, yes)


@app.command()
def tasks(
    path: Path = typer.Argument(Path("."), help="Тека проєкту"),
    backend: str = typer.Option("mock", "--backend", help="AI-бекенд: mock | claude"),
    model: str = typer.Option(None, "--model", help="Модель для claude-бекенду"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Перезаписати без підтвердження"),
) -> None:
    """Виведення задач delivery/tasks.md за plan.md (US-4, FR-005)."""
    bundle = _require_bundle(path)
    plan_file = bundle / "architecture" / "plan.md"
    if not plan_file.exists():
        typer.secho("❌ Немає plan.md — спершу `spec-forge plan`", fg=typer.colors.RED)
        raise typer.Exit(1)
    context = (
        "# Technical plan (plan.md)\n"
        + plan_file.read_text(encoding="utf-8")
        + "\n\nВиведи атомарні, трасовані задачі (tasks.md) у Markdown з галочками."
    )
    _run_phase(path, "tasks", "developer", context, "delivery/tasks.md", backend, model, yes)


@app.command()
def validate(path: Path = typer.Argument(Path("."), help="Тека проєкту")) -> None:
    """Прогнати quality gates по bundle (US-5, FR-006)."""
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
    typer.secho("Усі gates зелені.", fg=typer.colors.GREEN)


@app.command()
def deploy(path: Path = typer.Argument(Path("."), help="Тека проєкту")) -> None:
    """Root-symlinks для tool-discovery (US-6, FR-008)."""
    _require_bundle(path)
    created = deploy_root(path)
    mark_phase(path, "deploy")
    typer.secho(
        f"✅ Розгорнуто {len(created)} pointer-ів: {', '.join(created)}", fg=typer.colors.GREEN
    )


@app.command()
def export(
    path: Path = typer.Argument(Path("."), help="Тека проєкту"),
    out: str = typer.Option("exports", "--out", help="Тека для PDF"),
) -> None:
    """Експорт усіх файлів specifications/ у єдиний PDF з таймстемпом (FR-013)."""
    _require_bundle(path)
    pdf = export_bundle(path, out)
    typer.secho(f"✅ PDF-знімок: {pdf}", fg=typer.colors.GREEN)


@app.command()
def analyze(
    source: Path = typer.Argument(..., help="Тека НАЯВНОГО проєкту для аналізу коду"),
    path: Path = typer.Option(None, "--path", help="Куди писати specifications/ (типово = source)"),
    slug: str = typer.Option("002-existing", "--slug", help="Папка під product/specs/"),
    only: str = typer.Option("both", "--only", help="both | spec | review"),
    max_file_bytes: int = typer.Option(100_000, "--max-file-bytes", help="Ліміт на файл (байт)"),
    max_chars: int = typer.Option(200_000, "--max-chars", help="Ліміт контексту (символів)"),
    backend: str = typer.Option("mock", "--backend", help="AI-бекенд: mock | claude"),
    model: str = typer.Option(None, "--model", help="Модель для claude-бекенду"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Перезаписати без підтвердження"),
) -> None:
    """(Reverse) Спека + рев'ю НАЯВНОГО коду (brownfield). Реальний зміст — `--backend claude`."""
    if only not in ("both", "spec", "review"):
        raise typer.BadParameter("--only має бути: both | spec | review")
    if not source.is_dir():
        typer.secho(f"❌ Немає теки: {source}", fg=typer.colors.RED)
        raise typer.Exit(1)

    target = path or source
    bundle = target / "specifications"
    try:
        code_ctx = codescan.scan_codebase(source, max_file_bytes=max_file_bytes, max_total_chars=max_chars)
    except OSError as exc:
        typer.secho(f"❌ Скан коду: {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    if only in ("both", "spec"):
        ctx = _build_code_context(
            code_ctx, bundle,
            "Виведи ФАКТИЧНУ специфікацію продукту (spec.md) за цим кодом, з посиланнями на файли.",
        )
        _run_phase(target, "analyze", "reverse-analyst", ctx, f"product/specs/{slug}/spec.md", backend, model, yes)

    if only in ("both", "review"):
        inferred = bundle / "product" / "specs" / slug / "spec.md"
        extra = ""
        if inferred.exists():
            extra = "# Inferred spec (spec.md)\n" + inferred.read_text(encoding="utf-8")
        expected = _read_first_spec(bundle)
        if expected and (not inferred.exists() or expected != inferred.read_text(encoding="utf-8")):
            extra += "\n\n# Expected spec (наявна)\n" + expected
        ctx = _build_code_context(
            code_ctx, bundle,
            "Склади рев'ю/gap-документ: що реалізовано, чого бракує/невірно, ДЕ виправити "
            "(файл+секція), severity; вердикт чи все написано як треба.",
            extra=extra,
        )
        _run_phase(target, "review", "reviewer", ctx, f"product/specs/{slug}/review.md", backend, model, yes)


@app.command()
def status(path: Path = typer.Argument(Path("."), help="Тека проєкту")) -> None:
    """Показати прогрес життєвого циклу (FR-009)."""
    done = set(load_state(path).get("phases", []))
    for ph in PHASES:
        icon = "✅" if ph in done else "⬜"
        typer.secho(f"{icon} {ph}")
    nxt = next((p for p in PHASES if p not in done), None)
    if nxt:
        typer.secho(f"→ наступна фаза: {nxt}", fg=typer.colors.BLUE)
    else:
        typer.secho("Усі фази пройдено.", fg=typer.colors.GREEN)


@command_app.command("install")
def command_install(
    project: bool = typer.Option(False, "--project", help="У поточний проєкт замість глобально"),
) -> None:
    """Додати slash-команду /spec-forge (глобально або у проєкт)."""
    root = Path(".") if project else None
    path, created = integrations.ensure_installed(root)
    label = "додано" if created else "вже існує"
    typer.secho(f"✅ /spec-forge {label}: {path}", fg=typer.colors.GREEN)


@command_app.command("uninstall")
def command_uninstall(
    project: bool = typer.Option(False, "--project", help="З поточного проєкту замість глобально"),
) -> None:
    """Прибрати slash-команду /spec-forge."""
    root = Path(".") if project else None
    path, removed = integrations.remove(root)
    color = typer.colors.GREEN if removed else typer.colors.YELLOW
    label = "✅ прибрано" if removed else "= не було"
    typer.secho(f"{label}: {path}", fg=color)


if __name__ == "__main__":
    app()
