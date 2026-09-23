"""Independent regression cases from the organizers' dataset, not new rules."""

from copy import deepcopy
from itertools import permutations

import pytest

from engine.changes import describe_contributions
from engine.scoring import apply_effects, load_data, run


@pytest.mark.parametrize("measure,expected", [
    ("M1", {"T1": 4.5, "T2": 6.75}),
    ("M2", {"T1": 3, "B2": 2.25}),
    ("M3", {"T1": 8, "T2": 10, "E2": 2}),
    ("M4", {"E1": 9, "E2": 2.25, "B1": 1.5}),
    ("M5", {"E2": 8.75, "C1": 2.5}),
    ("M6", {"E1": 2.5, "E2": 1.5}),
    ("M7", {"S1": 10}),
    ("M8", {"S2": 8.75}),
    ("M9", {"S1": 2.625, "S2": 2.625, "B1": 2.625}),
    ("M10", {"B1": 10.5, "B2": 1.75}),
    ("M11", {"B2": 10.5, "T1": -1.75}),
    ("M12", {"C2": 4.375}),
    ("M13", {"C1": 9, "E2": 1}),
    ("M14", {"C1": 4.375, "C2": 1.75}),
])
def test_every_catalogue_measure_lag_and_scope(measure, expected):
    districts, initiatives, rules = load_data()
    initiative = next(row for row in initiatives if row["id"] == measure)
    city = initiative["type"] == "Город"
    decisions = [{"id": measure, "district": None if city else "Нура"}]
    before = deepcopy((districts, decisions, initiatives, rules))
    updated = apply_effects(districts, decisions, initiatives, rules)
    assert (districts, decisions, initiatives, rules) == before
    for old, new in zip(districts, updated):
        for indicator in rules["weights"]:
            delta = expected.get(indicator, 0) if city or old["name"] == "Нура" else 0
            assert new[indicator] - old[indicator] == pytest.approx(delta)
    trace = describe_contributions(decisions, initiatives, rules)
    assert trace[0]["effects_after_lag_before_clip"] == expected
    updated[0]["T1"] = -999
    assert districts == before[0]


@pytest.mark.parametrize("first,second,indicator", [
    ("M1", "M2", "T1"), ("M10", "M12", "B1"), ("M5", "M6", "E2"),
])
def test_synergy_bonus_is_exactly_two_only_in_target_district(first, second, indicator):
    districts, initiatives, rules = load_data()
    decisions = [{"id": first, "district": "Нура"}, {"id": second, "district": None}]
    with_bonus = apply_effects(districts, decisions, initiatives, rules)
    without_bonus = apply_effects(districts, decisions, initiatives, {**rules, "synergies": []})
    for plain, combined in zip(without_bonus, with_bonus):
        for field in rules["weights"]:
            bonus = 2 if combined["name"] == "Нура" and field == indicator else 0
            assert combined[field] - plain[field] == bonus


def test_all_120_orders_of_control_scenario_are_identical():
    _, _, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    expected = run(decisions)
    assert expected["score"] == pytest.approx(56.54307)
    for order in permutations(decisions):
        assert run(list(order)) == expected


def test_both_clip_limits_after_total_effect_and_bonus():
    districts, _, rules = load_data()
    initiatives = [
        {"id": "UP", "type": "Город", "lag": 0, "effects": {"T1": 200, "T2": -200}},
        {"id": "DOWN", "type": "Город", "lag": 0, "effects": {"T1": -30, "T2": 20}},
    ]
    decisions = [{"id": "UP"}, {"id": "DOWN"}]
    updated = apply_effects(districts, decisions, initiatives, rules)
    assert all(row["T1"] == 100 and row["T2"] == 0 for row in updated)
    assert updated == apply_effects(districts, list(reversed(decisions)), initiatives, rules)


def test_changing_a_valid_set_changes_score():
    _, _, rules = load_data()
    original = deepcopy(rules["known_results"]["example_valid_set"]["decisions"])
    changed = deepcopy(original)
    changed[-1] = {"id": "M4", "district": "Сарыарка"}
    assert run(changed)["valid"] is True
    assert run(changed)["score"] != run(original)["score"]
