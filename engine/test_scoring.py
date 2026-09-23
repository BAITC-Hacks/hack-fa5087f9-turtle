"""
Тесты против точных значений из ТЗ. Запуск: pytest engine/test_scoring.py
Не меняйте ожидаемые числа -- они даны организаторами, ваш код должен под них подстроиться.
"""

import pytest
from scoring import compute_score, load_data, run


def test_base_score_no_actions():
    result = run([])
    # base score без решений = 52.56 (см. data/rules.json -> known_results)
    assert result["valid"] is True
    assert abs(result["score"] - 52.56) < 0.05



def test_base_score_breakdown():
    districts, _, rules = load_data()
    result = compute_score(districts, rules)

    assert result["d_avg"] == pytest.approx(56.8624)
    assert result["district_scores"]["Нура"] == pytest.approx(49.18)
    assert result["min_district"] == "Нура"
    assert result["n_crit"] == 2
    assert result["score"] == pytest.approx(52.55768)


def test_critical_threshold_is_strict():
    districts, _, rules = load_data()
    districts[-1]["S1"] = 40
    districts[-1]["S2"] = 40

    result = compute_score(districts, rules)

    assert result["n_crit"] == 0

def test_example_valid_set():
    decisions = [
        {"id": "M7", "district": "Нура"},
        {"id": "M8", "district": "Нура"},
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
        {"id": "M5", "district": "Сарыарка"},
    ]
    result = run(decisions)
    assert result["valid"] is True
    assert abs(result["score"] - 56.5) < 0.5  # синергия M10+M12 должна сработать




def test_example_result_contains_ui_and_ai_data():
    decisions = [
        {"id": "M7", "district": "Нура"},
        {"id": "M8", "district": "Нура"},
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
        {"id": "M5", "district": "Сарыарка"},
    ]

    result = run(decisions)
    before = {district["name"]: district for district in result["before"]}
    after = {district["name"]: district for district in result["after"]}

    assert result["base_score"] == pytest.approx(52.55768)
    assert result["score_delta"] == pytest.approx(
        result["score"] - result["base_score"]
    )
    assert result["base_result"]["n_crit"] == 2
    assert before["Нура"]["S1"] == 38
    assert after["Нура"]["S1"] == pytest.approx(48)

def test_budget_exceeded_invalid():
    # Пример набора, который точно превышает бюджет 100 -- подставьте свой
    decisions = [
        {"id": "M3", "district": "Есиль"},
        {"id": "M13", "district": "Алматы"},
        {"id": "M7", "district": "Сарыарка"},
        {"id": "M8", "district": "Байконур"},
        {"id": "M5", "district": "Нура"},
    ]  # 30+28+24+20+25 = 127 > 100
    result = run(decisions)
    assert result["valid"] is False


def test_incompatible_pair_invalid():
    decisions = [
        {"id": "M1", "district": "Есиль"},
        {"id": "M3", "district": "Есиль"},  # M1 и M3 несовместимы
        {"id": "M9", "district": "Нура"},
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
    ]
    result = run(decisions)
    assert result["valid"] is False
