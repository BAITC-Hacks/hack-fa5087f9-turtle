from copy import deepcopy

import pytest

from engine.scoring import apply_effects, load_data


@pytest.fixture
def simulation_data():
    districts_data, initiatives, rules = load_data()
    districts = districts_data["districts"] if isinstance(districts_data, dict) else districts_data
    return districts, initiatives, rules


def by_name(districts):
    return {district["name"]: district for district in districts}


def test_example_effects_and_source_data_are_unchanged(simulation_data):
    districts, initiatives, rules = simulation_data
    original = deepcopy(districts)
    decisions = [
        {"id": "M7", "district": "Нура"},
        {"id": "M8", "district": "Нура"},
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
        {"id": "M5", "district": "Сарыарка"},
    ]

    updated = by_name(apply_effects(districts, decisions, initiatives, rules))

    assert districts == original
    assert updated["Нура"]["S1"] == pytest.approx(48)
    assert updated["Нура"]["S2"] == pytest.approx(43.75)
    assert updated["Нура"]["B1"] == pytest.approx(67.5)
    assert updated["Сарыарка"]["E2"] == pytest.approx(48.75)
    assert updated["Сарыарка"]["C1"] == pytest.approx(47.5)


def test_city_measure_applies_to_every_district(simulation_data):
    districts, initiatives, rules = simulation_data
    updated = by_name(
        apply_effects(districts, [{"id": "M12", "district": None}], initiatives, rules)
    )

    for district in districts:
        assert updated[district["name"]]["C2"] == pytest.approx(district["C2"] + 4.375)


def test_district_measure_does_not_change_other_districts(simulation_data):
    districts, initiatives, rules = simulation_data
    updated = by_name(
        apply_effects(districts, [{"id": "M7", "district": "Нура"}], initiatives, rules)
    )
    original = by_name(districts)

    assert updated["Нура"]["S1"] == pytest.approx(48)
    for district_name in original.keys() - {"Нура"}:
        assert updated[district_name]["S1"] == original[district_name]["S1"]


@pytest.mark.parametrize(
    ("decisions", "district", "indicator", "expected"),
    [
        ([{"id": "M1", "district": "Есиль"}, {"id": "M2", "district": None}], "Есиль", "T1", 54.5),
        ([{"id": "M10", "district": "Нура"}, {"id": "M12", "district": None}], "Нура", "B1", 67.5),
        ([{"id": "M5", "district": "Сарыарка"}, {"id": "M6", "district": None}], "Сарыарка", "E2", 52.25),
    ],
)
def test_synergy_is_applied_in_first_measure_district(
    simulation_data, decisions, district, indicator, expected
):
    districts, initiatives, rules = simulation_data
    updated = by_name(apply_effects(districts, decisions, initiatives, rules))
    assert updated[district][indicator] == pytest.approx(expected)


def test_decision_order_does_not_change_result(simulation_data):
    districts, initiatives, rules = simulation_data
    decisions = [
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
        {"id": "M5", "district": "Сарыарка"},
        {"id": "M6", "district": None},
    ]

    forward = apply_effects(districts, decisions, initiatives, rules)
    backward = apply_effects(districts, list(reversed(decisions)), initiatives, rules)
    assert forward == backward


def test_clip_happens_after_all_effects_are_summed(simulation_data):
    districts, _, rules = simulation_data
    initiatives = [
        {"id": "UP", "type": "Город", "lag": 0, "effects": {"T1": 70}},
        {"id": "DOWN", "type": "Город", "lag": 0, "effects": {"T1": -50}},
    ]
    decisions = [{"id": "UP", "district": None}, {"id": "DOWN", "district": None}]

    updated = by_name(apply_effects(districts, decisions, initiatives, rules))
    assert updated["Есиль"]["T1"] == pytest.approx(65)
