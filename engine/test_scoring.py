"""
Тесты против точных значений из ТЗ. Запуск: pytest engine/test_scoring.py
Не меняйте ожидаемые числа -- они даны организаторами, ваш код должен под них подстроиться.
"""

import pytest
from scoring import run


def test_base_score_no_actions():
    result = run([])
    # base score без решений = 52.56 (см. data/rules.json -> known_results)
    assert result["valid"] is True
    assert abs(result["score"] - 52.56) < 0.05


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
