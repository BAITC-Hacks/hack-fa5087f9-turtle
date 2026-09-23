"""Prepare source data and calculated results for an AI explanation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"


def build_context(
    decisions: list[dict],
    engine_result: dict[str, Any],
    initiatives: list[dict] | None = None,
    districts: list[dict] | None = None,
) -> dict[str, Any]:
    """Build an AI payload; all calculated numbers are copied from the engine result."""
    if initiatives is None:
        initiatives = json.loads((DATA_DIR / "initiatives.json").read_text(encoding="utf-8"))
    if districts is None:
        districts_data = json.loads((DATA_DIR / "districts.json").read_text(encoding="utf-8"))
        districts = districts_data["districts"]
    else:
        districts_data = json.loads((DATA_DIR / "districts.json").read_text(encoding="utf-8"))

    initiatives_by_id = {item["id"]: item for item in initiatives}
    districts_by_name = {item["name"]: item for item in districts}
    selected = []
    for decision in decisions:
        initiative = initiatives_by_id[decision["id"]]
        selected.append({
            "id": initiative["id"],
            "name": initiative["name"],
            "direction": initiative["direction"],
            "cost": initiative["cost"],
            "district": decision.get("district"),
        })

    before = engine_result.get("before")
    if before is None:
        before = districts
    result_fields = {
        key: engine_result.get(key)
        for key in ("score", "d_avg", "min_district", "n_crit", "district_scores")
    }
    return {
        "decisions": selected,
        "total_cost": sum(item["cost"] for item in selected),
        "base_result": engine_result.get("base_result"),
        **result_fields,
        "result": result_fields,
        "before": before,
        "after": engine_result.get("after"),
        "changes": engine_result.get("changes"),
        "synergies": engine_result.get("synergies"),
        "district_profiles": {
            name: districts_data.get("profiles", {}).get(name)
            for name in districts_by_name
            if name in {item.get("district") for item in decisions}
        },
    }
