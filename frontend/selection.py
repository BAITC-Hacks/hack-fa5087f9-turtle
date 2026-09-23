"""Streamlit widgets for selecting five city initiatives."""

from __future__ import annotations

import streamlit as st
from engine.scoring import validate_decisions


def render_selection(
    initiatives: list[dict],
    districts: list[dict],
    rules: dict,
) -> tuple[list[dict], int]:
    """Render five decision slots and return ``[{id, district}, ...]`` and cost."""
    names = {item["id"]: f'{item["id"]} — {item["name"]} ({item["cost"]} у.е.)' for item in initiatives}
    by_label = {label: initiative_id for initiative_id, label in names.items()}
    by_id = {item["id"]: item for item in initiatives}
    district_names = [item["name"] for item in districts]
    all_ids = list(names)
    decision_count = rules["num_decisions"]
    default_choices = [
        ("M7", "Нура"),
        ("M8", "Нура"),
        ("M10", "Нура"),
        ("M12", None),
        ("M5", "Сарыарка"),
    ]

    st.subheader("Выберите пять мероприятий")
    decisions = []
    total_cost = 0
    for slot in range(decision_count):
        key = f"decision_{slot}_label"
        default_id, default_district = default_choices[slot % len(default_choices)]
        if default_id not in by_id:
            default_id = all_ids[slot % len(all_ids)]
        if key not in st.session_state:
            st.session_state[key] = names[default_id]
        district_key = f"decision_{slot}_district"
        if district_key not in st.session_state and default_district in district_names:
            st.session_state[district_key] = default_district

        current_label = st.session_state.get(key, names[default_id])
        previous_id = by_label.get(current_label, all_ids[slot % len(all_ids)])
        previous_type = st.session_state.get(f"decision_{slot}_type")
        current_type = by_id[previous_id]["type"]
        if previous_type != current_type and current_type == "Город":
            st.session_state.pop(district_key, None)
        selected_label = st.selectbox(
            f"Решение {slot + 1}",
            options=list(names.values()),
            index=all_ids.index(previous_id),
            key=key,
            format_func=lambda label: label,
        )
        initiative_id = by_label[selected_label]
        initiative = by_id[initiative_id]
        if st.session_state.get(f"decision_{slot}_type") != initiative["type"] and initiative["type"] == "Город":
            st.session_state.pop(district_key, None)
        st.session_state[f"decision_{slot}_type"] = initiative["type"]
        district = None
        if initiative["type"] == "Район":
            district = st.selectbox(
                f"Район для решения {slot + 1}",
                options=district_names,
                key=district_key,
            )
        decisions.append({"id": initiative_id, "district": district})
        total_cost += initiative["cost"]

    budget = rules["budget"]
    st.sidebar.metric("Стоимость решений", f"{total_cost} у.е.")
    st.sidebar.metric("Остаток бюджета", f"{budget - total_cost} у.е.")
    st.sidebar.caption(f"Выбрано позиций: {len(decisions)} из {decision_count}")
    valid, reason = validate_decisions(decisions, initiatives, rules)
    if not valid:
        st.sidebar.error(reason)
    return decisions, total_cost
