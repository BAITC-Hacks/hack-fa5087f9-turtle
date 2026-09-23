"""Render engine facts separately from the model's qualitative interpretation."""

import json
import re


SECTIONS = {
    "improvements": "Что улучшилось",
    "remaining_problems": "Какие проблемы остались",
    "tradeoffs": "Какие компромиссы есть у выбранного набора",
}
RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "scenario_interpretation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {name: {"type": "string"} for name in SECTIONS},
            "required": list(SECTIONS),
            "additionalProperties": False,
        },
    },
}


def number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def synergy_texts(context: dict) -> list[str]:
    lines = []
    for synergy in context.get("synergies") or []:
        effects = synergy.get("effect")
        if effects is None and synergy.get("indicator"):
            effects = {synergy["indicator"]: synergy["bonus"]}
        place = f'в районе {synergy["district"]}' if synergy.get("district") else "во всём городе"
        for indicator, bonus in (effects or {}).items():
            lines.append(
                f'{" + ".join(synergy["pair"])} {place}: {indicator} +{number(bonus)}'
            )
    return lines


def engine_facts(context: dict) -> dict[str, list[str]]:
    """Formatting only; prices, deltas and scores are already computed in Python."""
    facts = {name: [] for name in SECTIONS}
    if context.get("score") is not None:
        text = f'Итоговый Score: {context["score"]:.2f}'
        if context.get("score_delta") is not None:
            text += f' ({context["score_delta"]:+.2f} к базе)'
        facts["improvements"].append(text + ".")
    changes = context.get("changes") or []
    positives = sorted((row for row in changes if row["delta"] > 0), key=lambda row: row["delta"], reverse=True)
    for row in positives[:3]:
        facts["improvements"].append(f'{row["district"]}: {row["indicator"]} +{number(row["delta"])}.')
    for text in synergy_texts(context):
        facts["improvements"].append("Синергия " + text + " (уже включена в изменения).")
    if context.get("n_crit") is not None:
        threshold = context.get("critical_threshold")
        label = f"строго ниже {number(threshold)}" if threshold is not None else "ниже критического порога"
        facts["remaining_problems"].append(f'Значений {label}: {context["n_crit"]}.')
    weakest = context.get("min_district")
    if weakest:
        value = (context.get("district_scores") or {}).get(weakest)
        suffix = f" — {number(value)}" if value is not None else ""
        facts["remaining_problems"].append(f"Самый низкий балл района: {weakest}{suffix}.")
    for row in sorted((row for row in changes if row["delta"] < 0), key=lambda row: row["delta"])[:3]:
        facts["tradeoffs"].append(f'{row["district"]}: {row["indicator"]} {number(row["delta"])}.')
    if context.get("total_cost") is not None and context.get("budget") is not None:
        text = f'Стоимость: {number(context["total_cost"])} из {number(context["budget"])} у.е.'
        if context.get("budget_remaining") is not None:
            text += f'; остаток: {number(context["budget_remaining"])} у.е.'
        facts["tradeoffs"].append(text + ".")
    lags = [f'{item["id"]}: {number(item["lag"])}' for item in context.get("decisions", []) if item.get("lag") is not None]
    if lags:
        facts["tradeoffs"].append("Лаги мер в кварталах: " + "; ".join(lags) + ".")
    if context.get("horizon_quarters") is not None:
        facts["tradeoffs"].append(f'Горизонт модели: {number(context["horizon_quarters"])} кварталов. Лаги уже учтены в изменениях.')
    return facts


def render_response(content: str, context: dict) -> str:
    """Reject malformed responses and numeric claims before showing model text."""
    paragraphs = json.loads(content)
    if not isinstance(paragraphs, dict) or set(paragraphs) != set(SECTIONS):
        raise ValueError("Unexpected explanation schema")
    metadata_present = context.get("total_cost") is not None and any(
        item.get("lag") is not None for item in context.get("decisions", [])
    )
    for paragraph in paragraphs.values():
        if not isinstance(paragraph, str) or not paragraph.strip() or len(paragraph) > 1200:
            raise ValueError("Missing or oversized interpretation")
        if re.search(r"\d", paragraph):
            raise ValueError("Numeric claims must come from the engine")
        if metadata_present:
            missing = r"(?:нет|отсутств\w*|не\s+(?:указ\w*|передан\w*|извест\w*|предостав\w*)|недостаточно)"
            topic = r"(?:стоим\w*|бюдж\w*|цен\w*|лаг\w*|срок\w*)"
            if re.search(rf"{missing}.{{0,70}}{topic}|{topic}.{{0,70}}{missing}", paragraph, re.IGNORECASE):
                raise ValueError("Provided metadata was described as missing")
    facts = engine_facts(context)
    return "\n\n".join(
        f"### {title}\n\n" + " ".join(facts[name]) + f"\n\n{paragraphs[name].strip()}"
        for name, title in SECTIONS.items()
    )
