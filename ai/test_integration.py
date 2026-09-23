"""Regression checks for the full engine -> context -> API -> explanation path."""

from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import Mock

try:
    import httpx2 as httpx  # OpenAI SDK 3.x
except ImportError:
    import httpx  # OpenAI SDK 1.x/2.x
import pytest
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError

from ai import explain
from ai.context import build_context
from ai.prompt import build_user_prompt
from ai.response import render_response
from ai.test_explain import MODEL_PARAGRAPHS, completion_response
from engine.scoring import load_data, run


@pytest.fixture
def context():
    districts, initiatives, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    return build_context(decisions, run(decisions), initiatives, districts, rules)


def test_context_has_real_final_deltas_cost_lags_and_synergy(context):
    original = deepcopy(context)
    payload = json.loads(build_user_prompt(context).split("КОНТЕКСТ СИМУЛЯЦИИ:\n")[1])
    assert payload["total_cost"] == 95
    assert payload["budget_remaining"] == 5
    assert payload["budget"] == 100
    assert payload["critical_values"] == []
    assert [item["lag"] for item in payload["decisions"]] == [3, 3, 1, 1, 3]
    assert all("effects" not in item for item in payload["decisions"])
    changes = {(row["district"], row["indicator"]): row["delta"] for row in payload["changes"]}
    assert changes["Нура", "B1"] == 12.5
    assert changes["Нура", "S1"] == 10
    assert changes["Нура", "S2"] == 8.75
    assert changes["Сарыарка", "E2"] == 8.75
    assert changes["Нура", "C2"] == 4.38
    assert payload["synergies"] == [{"pair": ["M10", "M12"], "district": "Нура", "effect": {"B1": 2}}]
    assert context == original


def test_rendered_live_answer_copies_facts_and_never_adds_synergy_twice(context):
    text = render_response(json.dumps(MODEL_PARAGRAPHS), context)
    assert "56.54 (+3.99 к базе)" in text
    assert "Нура: B1 +12.5" in text
    assert "B1 +2 (уже включена в изменения)" in text
    assert "95 из 100 у.е.; остаток: 5" in text
    assert "M7: 3" in text
    assert "ниже 40: 0" in text


@pytest.mark.parametrize("bad_text", [
    "Нура: B1 +14.5.",
    "Нет данных о стоимости и лагах.",
    "Сведения о стоимости отсутствуют.",
])
def test_rejects_invented_numbers_or_false_missing_metadata(context, bad_text):
    paragraphs = {**MODEL_PARAGRAPHS, "tradeoffs": bad_text}
    with pytest.raises(ValueError):
        render_response(json.dumps(paragraphs), context)


@pytest.mark.parametrize("response", [
    completion_response("not JSON"),
    completion_response('{"improvements":"something"}'),
    completion_response(finish_reason="length"),
    completion_response(json.dumps({**MODEL_PARAGRAPHS, "tradeoffs": "Цена 999 у.е."})),
])
def test_invalid_or_truncated_ai_answer_falls_back(monkeypatch, context, response):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.return_value = response
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    answer = explain.explain_result(context, [])
    assert answer.startswith("Резервное объяснение без AI")
    assert "56.54" in answer and "B1 +2" in answer
    assert "999" not in answer


@pytest.mark.parametrize("error", [
    APITimeoutError(request=httpx.Request("POST", "https://api.openai.com")),
    APIConnectionError(request=httpx.Request("POST", "https://api.openai.com")),
    AuthenticationError("private detail", response=httpx.Response(401, request=httpx.Request("POST", "https://api.openai.com")), body=None),
    RateLimitError("private detail", response=httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com")), body=None),
])
def test_real_sdk_error_classes_return_grounded_fallback(monkeypatch, context, error):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.side_effect = error
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    answer = explain.explain_result(context, [])
    assert answer.startswith("Резервное объяснение без AI")
    assert "95 из 100" in answer and "Нура: B1 +12.5" in answer
    assert "M10 + M12 в районе Нура: B1 +2" in answer
    assert "private detail" not in answer


def test_offline_demo_never_creates_api_client(monkeypatch, context):
    factory = Mock(side_effect=AssertionError("Unexpected API request"))
    monkeypatch.setattr(explain, "OpenAI", factory)
    assert "демонстрационный режим" in explain.explain_result(context, [], offline=True)
    factory.assert_not_called()


def test_model_override_reaches_api(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.return_value = completion_response()
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    assert not explain.explain_result(context, [], model="gpt-4.1").startswith("Резервное")
    assert client.chat.completions.create.call_args.kwargs["model"] == "gpt-4.1"
