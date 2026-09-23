"""Explanation priorities come from final engine deltas, not a fixed scenario."""

from copy import deepcopy
import json

from ai.context import build_context
from ai.prompt import build_user_prompt
from ai.response import render_response
from ai.test_explain import MODEL_PARAGRAPHS
from engine.scoring import load_data, run


def payload(context):
    return json.loads(build_user_prompt(context).split("КОНТЕКСТ СИМУЛЯЦИИ:\n")[1])


def test_control_focus_names_real_top_improvements_without_mutating_context():
    _, _, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    context = build_context(decisions, run(decisions))
    original = deepcopy(context)
    focus = payload(context)["explanation_focus"]
    assert [(row["district"], row["indicator"], row["delta"]) for row in focus["top_improvements"]] == [
        ("Нура", "B1", 12.5), ("Нура", "S1", 10), ("Сарыарка", "E2", 8.75),
    ]
    assert [row["indicator_name"] for row in focus["top_improvements"]] == [
        "безопасность улиц", "школы и детские сады", "качество воздуха",
    ]
    answer = render_response(json.dumps(MODEL_PARAGRAPHS), context)
    assert "B1 +12.5 — безопасность улиц" in answer
    assert "E2 +8.75 — качество воздуха" in answer
    assert context == original


def test_focus_changes_with_input_and_preserves_observed_decreases():
    context = {"changes": [
        {"district": "Алматы", "indicator": "C1", "delta": 7},
        {"district": "Есиль", "indicator": "T1", "delta": 9},
        {"district": "Нура", "indicator": "S1", "delta": 0},
        {"district": "Есиль", "indicator": "E1", "delta": -2},
    ]}
    focus = payload(context)["explanation_focus"]
    assert [row["indicator"] for row in focus["top_improvements"]] == ["T1", "C1"]
    assert focus["observed_decreases"] == [context["changes"][-1]]


def test_empty_focus_does_not_invent_improvements():
    assert payload({})["explanation_focus"] == {"top_improvements": [], "observed_decreases": []}
