"""Prepare source data and calculated results for an AI explanation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.changes import describe_changes, describe_contributions

DATA_DIR = Path(__file__).parent.parent / "data"


def build_context(
    decisions: list[dict],
    engine_result: dict[str, Any],
    initiatives: list[dict] | None = None,
    districts: list[dict] | None = None,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an AI payload; all calculated numbers are copied from the engine result."""
    if initiatives is None:
        initiatives = json.loads((DATA_DIR / "initiatives.json").read_text(encoding="utf-8"))
    if districts is None:
        districts_data = json.loads((DATA_DIR / "districts.json").read_text(encoding="utf-8"))
        districts = districts_data["districts"]
    else:
        districts_data = json.loads((DATA_DIR / "districts.json").read_text(encoding="utf-8"))
    if rules is None:
        rules = json.loads((DATA_DIR / "rules.json").read_text(encoding="utf-8"))

    initiatives_by_id = {item["id"]: item for item in initiatives}
    districts_by_name = {item["name"]: item for item in districts}
    selected = []
    for decision in decisions:
        initiative = initiatives_by_id[decision["id"]]
        selected.append({
            "id": initiative["id"],
            "name": initiative["name"],
            "direction": initiative["direction"],
            "type": initiative["type"],
            "cost": initiative["cost"],
            "district": decision.get("district"),
            "lag": initiative["lag"],
            "effects": initiative["effects"],
        })

    before = engine_result.get("before")
    if before is None:
        before = districts
    result_fields = {
        key: engine_result.get(key)
        for key in (
            "score",
            "score_delta",
            "d_avg",
            "min_district",
            "n_crit",
            "critical_values",
            "district_scores",
        )
    }
    synergies = engine_result.get("synergies")
    if synergies is None:
        decisions_by_id = {decision["id"]: decision for decision in decisions}
        synergies = []
        for synergy in rules.get("synergies", []):
            first_id, second_id = synergy["pair"]
            if first_id not in decisions_by_id or second_id not in decisions_by_id:
                continue
            synergies.append({
                "pair": [first_id, second_id],
                "district": (
                    decisions_by_id[first_id].get("district")
                    if synergy.get("applies_to") == "district_of_first"
                    else None
                ),
                "effect": synergy["effect"],
            })
    changes = engine_result.get("changes")
    if changes is None and engine_result.get("after") is not None:
        changes = describe_changes(before, engine_result["after"], decisions, rules)["changes"]
    critical_values = (
        [{"district": row["district"], "indicator": row["indicator"], "value": row["after"]}
         for row in changes if row["after"] < rules["critical_threshold"]]
        if changes is not None else engine_result.get("critical_values")
    )
    result_fields["critical_values"] = critical_values
    total_cost = sum(item["cost"] for item in selected)
    return {
        "decisions": selected,
        "total_cost": total_cost,
        "budget": rules.get("budget"),
        "budget_remaining": rules["budget"] - total_cost,
        "horizon_quarters": rules["horizon_quarters"],
        "critical_threshold": rules["critical_threshold"],
        "realized_contributions": describe_contributions(decisions, initiatives, rules),
        "base_result": engine_result.get("base_result"),
        **result_fields,
        "result": result_fields,
        "before": before,
        "after": engine_result.get("after"),
        "changes": changes,
        "synergies": synergies,
        "district_profiles": {
            name: districts_data.get("profiles", {}).get(name)
            for name in districts_by_name
        },
    }
