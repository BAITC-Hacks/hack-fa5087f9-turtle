"""Подготовка изменений районов и синергий для интерфейса и AI-контекста."""


def describe_changes(
    before: list[dict],
    after: list[dict],
    decisions: list[dict],
    rules: dict,
) -> dict:
    """Возвращает неокруглённые изменения показателей и активные синергии."""
    before_by_name = {district["name"]: district for district in before}
    after_by_name = {district["name"]: district for district in after}
    indicators = tuple(rules["weights"])
    threshold = rules["critical_threshold"]

    changes = []
    for district_name, original in before_by_name.items():
        updated = after_by_name[district_name]
        for indicator in indicators:
            previous = original[indicator]
            current = updated[indicator]
            changes.append(
                {
                    "district": district_name,
                    "indicator": indicator,
                    "before": previous,
                    "after": current,
                    "delta": current - previous,
                    "critical": current < threshold,
                }
            )

    decisions_by_id = {decision["id"]: decision for decision in decisions}
    synergies = []
    for synergy in rules.get("synergies", []):
        first_id, second_id = synergy["pair"]
        if first_id not in decisions_by_id or second_id not in decisions_by_id:
            continue

        district = None
        if synergy.get("applies_to") == "district_of_first":
            district = decisions_by_id[first_id].get("district")

        for indicator, bonus in synergy["effect"].items():
            synergies.append(
                {
                    "pair": [first_id, second_id],
                    "district": district,
                    "indicator": indicator,
                    "bonus": bonus,
                }
            )

    return {"changes": changes, "synergies": synergies}
