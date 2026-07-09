from spec_forge.backends import ClaudeBackend, MockBackend, get_backend

import pytest


def test_get_backend_mock():
    assert isinstance(get_backend("mock"), MockBackend)


def test_get_backend_claude_default_model():
    be = get_backend("claude")
    assert isinstance(be, ClaudeBackend)
    assert be.model == "claude-opus-4-8"


def test_get_backend_claude_custom_model():
    assert get_backend("claude", "claude-sonnet-5").model == "claude-sonnet-5"


def test_get_backend_unknown_raises():
    with pytest.raises(ValueError):
        get_backend("gpt")


def test_mock_draft_contains_persona_and_context():
    out = MockBackend().draft("business-analyst", "hello world")
    assert "business-analyst" in out
    assert "hello world" in out
