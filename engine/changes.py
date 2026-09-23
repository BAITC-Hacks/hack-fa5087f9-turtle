"""Подготовка изменений районов и синергий для интерфейса и AI-контекста."""


def describe_contributions(decisions: list[dict], initiatives: list[dict], rules: dict) -> list[dict]:
    """Individual contributions after lag, before the final clip and synergies.

    These are not final deltas: several measures and synergies may affect one
    indicator, and the final value is clipped only after summing them all.
    """
    by_id = {item["id"]: item for item in initiatives}
    horizon = rules["horizon_quarters"]
    return [
        {
            "id": decision["id"],
            "district": decision.get("district"),
            "scope": by_id[decision["id"]]["type"],
            "effects_after_lag_before_clip": {
                indicator: effect * (horizon - by_id[decision["id"]]["lag"]) / horizon
                for indicator, effect in by_id[decision["id"]]["effects"].items()
            },
        }
        for decision in decisions
    ]


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

        synergies.append(
            {
                "pair": [first_id, second_id],
                "district": district,
                "effect": dict(synergy["effect"]),
            }
        )

    return {"changes": changes, "synergies": synergies}
