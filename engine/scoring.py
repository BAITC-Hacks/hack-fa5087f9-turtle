"""
Движок расчёта Astana Quality of Life Score.
Владелец фичи: [впишите имя]

Формула (см. /data/rules.json и README.md):
  1. I'_dk = clip(I_dk + sum(effect_m,k * (8 - lag_m)/8) + synergies, 0, 100)
  2. D_d = sum(w_k * I'_dk)  -- оценка района
  3. D_avg = sum(pop_share_d * D_d)  -- средневзвешенный по городу
  4. Score = 0.7 * D_avg + 0.3 * min(D_d) - 1.0 * N_crit
     N_crit = число пар (район, показатель) со значением < 40 после эффектов

Проверочные значения (из data/rules.json -> known_results):
  - базовый Score без решений: 52.56
  - пример валидного набора (M7/Нура, M8/Нура, M10/Нура, M12/город, M5/Сарыарка): Score ≈ 56.5
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_data():
    districts = json.loads((DATA_DIR / "districts.json").read_text())
    initiatives = json.loads((DATA_DIR / "initiatives.json").read_text())
    rules = json.loads((DATA_DIR / "rules.json").read_text())
    return districts, initiatives, rules


def validate_decisions(decisions: list[dict], initiatives: list[dict], rules: dict) -> tuple[bool, str]:
    """
    decisions: [{"id": "M7", "district": "Нура" | None}, ...]
    Проверяет: бюджет, ровно 5 решений, без повторов, район указан где нужно,
    не более 2 на направление, несовместимости.
    Возвращает (is_valid, reason_if_invalid).
    """
    # TODO: реализовать по правилам из data/rules.json
    raise NotImplementedError


def apply_effects(districts: list[dict], decisions: list[dict], initiatives: list[dict], rules: dict) -> list[dict]:
    """
    Возвращает новые значения показателей по районам после применения эффектов
    (с учётом лага и синергий), обрезанные в [0, 100].
    """
    # TODO: реализовать шаг 1 формулы
    raise NotImplementedError


def compute_score(updated_districts: list[dict], rules: dict) -> dict:
    """
    Возвращает {"score": float, "d_avg": float, "min_district": str, "n_crit": int, "district_scores": {...}}
    """
    # TODO: реализовать шаги 2-4 формулы
    raise NotImplementedError


def run(decisions: list[dict]) -> dict:
    """Точка входа: валидация -> применение эффектов -> расчёт score."""
    districts, initiatives, rules = load_data()
    ok, reason = validate_decisions(decisions, initiatives, rules)
    if not ok:
        return {"valid": False, "reason": reason}
    updated = apply_effects(districts, decisions, initiatives, rules)
    result = compute_score(updated, rules)
    result["valid"] = True
    return result


if __name__ == "__main__":
    # Быстрая проверка на примере из ТЗ
    example = [
        {"id": "M7", "district": "Нура"},
        {"id": "M8", "district": "Нура"},
        {"id": "M10", "district": "Нура"},
        {"id": "M12", "district": None},
        {"id": "M5", "district": "Сарыарка"},
    ]
    print(run(example))
