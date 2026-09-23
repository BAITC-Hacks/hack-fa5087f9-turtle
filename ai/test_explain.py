import os
import json
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

MODEL_PARAGRAPHS = {
    "improvements": "Выбранный набор улучшает безопасность и социальную инфраструктуру Нуры.",
    "remaining_problems": "Отсутствие критических значений не означает устранение всех городских проблем.",
    "tradeoffs": "Средства направлены на выбранные приоритеты, а сроки мер ограничивают реализованный эффект.",
}


def completion_response(content=None, finish_reason="stop"):
    return SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content or json.dumps(MODEL_PARAGRAPHS, ensure_ascii=False)),
        finish_reason=finish_reason,
    )])


def test_missing_key_returns_grounded_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(explain, "ENV_FILE", tmp_path / ".env")
    client_factory = Mock(side_effect=AssertionError("API client must not be created"))
    monkeypatch.setattr(explain, "OpenAI", client_factory)

    answer = explain.explain_result(SAMPLE_CONTEXT, [])

    assert "Резервное объяснение без AI" in answer
    assert "56.54" in answer
    assert "+3.98" in answer
    assert "Нура: B1 +12.5" in answer
    assert "95 из 100" in answer
    assert "M10 + M12 в районе Нура: B1 +2" in answer
    assert "AI пока не подключён" in answer
    assert "у.е.." not in answer
    assert "OPENAI_API_KEY" not in answer and ".env" not in answer
    client_factory.assert_not_called()


def test_key_can_be_loaded_from_local_env(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test-from-env\n", encoding="utf-8")
    monkeypatch.setattr(explain, "ENV_FILE", env_file)
    completion = completion_response()
    create = Mock(return_value=completion)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))

    assert MODEL_PARAGRAPHS["improvements"] in explain.explain_result(SAMPLE_CONTEXT, [])
    assert os.environ["OPENAI_API_KEY"] == "test-from-env"


def test_successful_api_response_uses_grounded_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    completion = completion_response()
    create = Mock(return_value=completion)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(explain, "OpenAI", client_factory)

    answer = explain.explain_result(SAMPLE_CONTEXT, [])

    assert MODEL_PARAGRAPHS["improvements"] in answer
    assert "Score: 56.54 (+3.98 к базе)" in answer
    assert "Стоимость: 95 из 100" in answer
    assert "M10 + M12 в районе Нура: B1 +2" in answer
    assert client_factory.call_args.kwargs["timeout"] == 20.0
    assert client_factory.call_args.kwargs["max_retries"] == 0
    assert create.call_args.kwargs["messages"][0]["content"] == explain.SYSTEM_PROMPT
    assert "56.54" in create.call_args.kwargs["messages"][1]["content"]
    assert create.call_args.kwargs["response_format"]["json_schema"]["strict"] is True


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
