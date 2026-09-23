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
    if not isinstance(decisions, list):
        return False, "Решения должны быть списком из 5 мероприятий."
    required = rules.get("num_decisions", 5)
    if len(decisions) != required:
        return False, f"Нужно выбрать ровно {required} мероприятий; сейчас выбрано {len(decisions)}."

    by_id = {item.get("id"): item for item in initiatives}
    try:
        districts_data = json.loads((DATA_DIR / "districts.json").read_text(encoding="utf-8"))
        known_districts = {item["name"] for item in districts_data["districts"]}
    except (OSError, ValueError, KeyError, TypeError):
        return False, "Не удалось загрузить список районов для проверки решений."

    ids = []
    selected = []
    direction_counts = {}
    total_cost = 0
    for index, decision in enumerate(decisions, start=1):
        if not isinstance(decision, dict):
            return False, f"Решение №{index} должно содержать ID мероприятия и район."
        initiative_id = decision.get("id")
        if not isinstance(initiative_id, str):
            return False, f"Решение №{index}: укажите ID мероприятия текстом."
        if initiative_id not in by_id:
            return False, f"Решение №{index}: неизвестное мероприятие «{initiative_id}»."
        if initiative_id in ids:
            return False, f"Мероприятие {initiative_id} выбрано больше одного раза."

        initiative = by_id[initiative_id]
        district = decision.get("district")
        if initiative.get("type") == "Район":
            if not isinstance(district, str) or district not in known_districts:
                return False, f"Для мероприятия {initiative_id} укажите существующий район."
        elif initiative.get("type") == "Город":
            if district is not None:
                return False, f"Для городского мероприятия {initiative_id} район указывать нельзя."
        else:
            return False, f"У мероприятия {initiative_id} неизвестный тип размещения."

        ids.append(initiative_id)
        selected.append((initiative, district))
        direction = initiative.get("direction")
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
        total_cost += initiative.get("cost", 0)

    limit = rules.get("max_per_direction", 2)
    for direction, count in direction_counts.items():
        if count > limit:
            return False, f"В направлении «{direction}» выбрано {count} мероприятия; максимум — {limit}."

    budget = rules.get("budget", 100)
    if total_cost > budget:
        return False, f"Превышен бюджет: стоимость {total_cost} у.е., доступно {budget} у.е."

    chosen = {initiative_id for initiative_id in ids}
    selected_district = {initiative["id"]: district for initiative, district in selected}
    for pair in rules.get("incompatible_pairs", []):
        if len(pair) != 2 or not set(pair).issubset(chosen):
            continue
        first, second = pair
        # M1/M3 являются альтернативами по всему городу; остальные пары
        # конфликтуют только при попытке разместить обе меры в одном районе.
        if {first, second} == {"M1", "M3"} or selected_district.get(first) == selected_district.get(second):
            return False, f"Мероприятия {first} и {second} несовместимы в выбранных районах."

    return True, ""


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
