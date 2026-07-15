"""Project lifecycle state (.spec-forge/state.json) + phase order (FR-009).

The state lives in the root of the target project (outside the bundle), so it does not affect
scaffold determinism. It is used to: show progress (`status`) and support re-spec mode (FR-012):
a phase writes the first draft freely; a repeat run = update → diff + confirmation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PHASES = ["init", "spec", "plan", "tasks", "validate", "deploy"]
_STATE_REL = Path(".spec-forge") / "state.json"


def _state_path(root: Path) -> Path:
    return root / _STATE_REL


def load_state(root: Path) -> dict:
    path = _state_path(root)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"phases": [], "updated": None}


def phase_done(root: Path, phase: str) -> bool:
    return phase in load_state(root).get("phases", [])


def mark_phase(root: Path, phase: str) -> dict:
    state = load_state(root)
    phases = state.setdefault("phases", [])
    if phase not in phases:
        phases.append(phase)
    state["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state
