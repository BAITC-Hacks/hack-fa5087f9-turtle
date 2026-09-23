"""Do not confuse valid interpretation with missing metadata or invented numbers."""

import json
from unittest.mock import Mock

import pytest

from ai import explain
from ai.context import build_context
from ai.response import render_response
from ai.test_explain import MODEL_PARAGRAPHS, completion_response
from engine.scoring import load_data, run


@pytest.fixture
def context():
    _, _, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    return build_context(decisions, run(decisions))


@pytest.mark.parametrize("paragraph", [
    "Критических значений нет. Стоимость укладывается в бюджет.",
    "Стоимость укладывается в бюджет, критических значений нет.",
    "Бюджет распределён между выбранными мерами. Ухудшений нет.",
    "Лаги уже учтены, дополнительных сведений об исполнении нет.",
    "Меры M10 и M12 совместно улучшают B1 в Нуре.",
])
def test_accepts_valid_interpretation(context, paragraph):
    answer = render_response(json.dumps({**MODEL_PARAGRAPHS, "tradeoffs": paragraph}), context)
    assert paragraph in answer
    assert "56.54 (+3.99 к базе)" in answer


@pytest.mark.parametrize("paragraph", [
    "Стоимость неизвестна.",
    "Данные о бюджете не предоставлены.",
    "Нет данных о лагах.",
    "Стоимость не указана.",
    "Мера M99 улучшает город.",
    "Меры M10 и M12 дают B1 +14.5.",
])
def test_still_rejects_false_metadata_and_numeric_claims(context, paragraph):
    with pytest.raises(ValueError):
        render_response(json.dumps({**MODEL_PARAGRAPHS, "tradeoffs": paragraph}), context)


def test_repairs_rejected_response_once_without_showing_it(monkeypatch, context, caplog):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.side_effect = [
        completion_response(json.dumps({**MODEL_PARAGRAPHS, "tradeoffs": "Цена 999 у.е."})),
        completion_response(),
    ]
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    answer = explain.explain_result(context, [])
    assert not answer.startswith("Резервное")
    assert "999" not in answer
    assert client.chat.completions.create.call_count == 2
    assert "Numeric claims" in caplog.text
    assert "test-key" not in caplog.text and "999" not in caplog.text


def test_repeated_rejection_stops_after_two_requests(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.return_value = completion_response(
        json.dumps({**MODEL_PARAGRAPHS, "tradeoffs": "Цена 999 у.е."})
    )
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    answer = explain.explain_result(context, [])
    assert answer.startswith("Резервное")
    assert "999" not in answer
    assert client.chat.completions.create.call_count == 2
