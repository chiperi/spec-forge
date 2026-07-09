from spec_forge.state import load_state, mark_phase, phase_done


def test_mark_and_query(tmp_path):
    assert not phase_done(tmp_path, "spec")
    mark_phase(tmp_path, "init")
    mark_phase(tmp_path, "spec")
    assert phase_done(tmp_path, "spec")
    assert load_state(tmp_path)["phases"] == ["init", "spec"]
    assert (tmp_path / ".spec-forge" / "state.json").exists()


def test_mark_is_idempotent(tmp_path):
    mark_phase(tmp_path, "spec")
    mark_phase(tmp_path, "spec")
    assert load_state(tmp_path)["phases"] == ["spec"]
