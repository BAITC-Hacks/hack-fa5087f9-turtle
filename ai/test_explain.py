from types import SimpleNamespace
from unittest.mock import Mock

from ai import explain


SAMPLE_CONTEXT = {
    "valid": True,
    "score": 56.54,
    "score_delta": 3.98,
    "n_crit": 0,
    "total_cost": 95,
    "budget": 100,
    "decisions": [
        {"id": "M10", "name": "Освещение и камеры", "district": "Нура"},
        {"id": "M12", "name": "Платформа обращений", "district": None},
    ],
    "changes": [
        {"district": "Нура", "indicator": "B1", "before": 55, "after": 67.5, "delta": 12.5},
    ],
    "synergies": [
        {"pair": ["M10", "M12"], "district": "Нура", "indicator": "B1", "bonus": 2},
    ],
}


def test_missing_key_returns_grounded_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client_factory = Mock(side_effect=AssertionError("API client must not be created"))
    monkeypatch.setattr(explain, "OpenAI", client_factory)

    answer = explain.explain_result(SAMPLE_CONTEXT, [])

    assert "Резервное объяснение без AI" in answer
    assert "56.54" in answer
    assert "+3.98" in answer
    assert "Нура: B1 +12.5" in answer
    assert "95 из 100" in answer
    assert "M10 + M12 в районе Нура: B1 +2" in answer
    client_factory.assert_not_called()


def test_successful_api_response_uses_grounded_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    completion = Mock()
    completion.choices = [SimpleNamespace(message=SimpleNamespace(content="Улучшились показатели Нуры."))]
    create = Mock(return_value=completion)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(explain, "OpenAI", client_factory)

    answer = explain.explain_result(SAMPLE_CONTEXT, [])

    assert answer == "Улучшились показатели Нуры."
    assert client_factory.call_args.kwargs["timeout"] == 20.0
    assert client_factory.call_args.kwargs["max_retries"] == 0
    assert create.call_args.kwargs["messages"][0]["content"] == explain.SYSTEM_PROMPT
    assert "56.54" in create.call_args.kwargs["messages"][1]["content"]


def test_api_error_returns_fallback_without_leaking_exception(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    create = Mock(side_effect=RuntimeError("secret test detail"))
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))

    answer = explain.explain_result(SAMPLE_CONTEXT, [])

    assert "Резервное объяснение без AI" in answer
    assert "56.54" in answer
    assert "secret test detail" not in answer


def test_invalid_result_never_calls_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client_factory = Mock(side_effect=AssertionError("invalid input must not call API"))
    monkeypatch.setattr(explain, "OpenAI", client_factory)

    answer = explain.explain_result({"valid": False, "reason": "Превышен бюджет."}, [])

    assert answer == "Набор решений не прошёл проверку: Превышен бюджет."
    client_factory.assert_not_called()
