"""Local configuration failures must not break a calculated scenario."""

from unittest.mock import Mock

import pytest

from ai import explain
from ai.test_explain import SAMPLE_CONTEXT, completion_response


@pytest.mark.parametrize("error", [PermissionError("private path"), UnicodeDecodeError("utf-8", b"\xff", 0, 1, "private detail")])
def test_unreadable_env_returns_fallback_without_exposing_details(monkeypatch, error):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(explain, "ENV_FILE", Mock(read_text=Mock(side_effect=error)))
    factory = Mock(side_effect=AssertionError("must not call API"))
    monkeypatch.setattr(explain, "OpenAI", factory)
    assert explain.configured_model() == "gpt-4o-mini"
    answer = explain.explain_result(SAMPLE_CONTEXT, [])
    assert "Не удалось прочитать локальный .env" in answer
    assert "56.54" in answer and "95 из 100" in answer
    assert "private" not in answer
    factory.assert_not_called()


def test_environment_key_still_works_if_optional_env_file_is_unreadable(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-environment-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1")
    monkeypatch.setattr(explain, "ENV_FILE", Mock(read_text=Mock(side_effect=PermissionError)))
    client = Mock()
    client.chat.completions.create.return_value = completion_response()
    factory = Mock(return_value=client)
    monkeypatch.setattr(explain, "OpenAI", factory)
    answer = explain.explain_result(SAMPLE_CONTEXT, [])
    assert not answer.startswith("Резервное")
    assert factory.call_args.kwargs["api_key"] == "test-environment-key"
    assert client.chat.completions.create.call_args.kwargs["model"] == "gpt-4.1"


def test_blank_key_and_model_are_handled_as_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "   ")
    monkeypatch.setenv("OPENAI_MODEL", "   ")
    monkeypatch.setattr(explain, "ENV_FILE", tmp_path / "absent.env")
    factory = Mock(side_effect=AssertionError("must not call API"))
    monkeypatch.setattr(explain, "OpenAI", factory)
    assert explain.configured_model() == "gpt-4o-mini"
    assert "Ключ OpenAI не найден" in explain.explain_result(SAMPLE_CONTEXT, [])
    factory.assert_not_called()
