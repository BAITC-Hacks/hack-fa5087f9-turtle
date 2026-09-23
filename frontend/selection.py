"""Streamlit widgets for selecting five city initiatives."""

from __future__ import annotations

import streamlit as st


def render_selection(initiatives: list[dict], districts: list[dict]) -> tuple[list[dict], int]:
    """Render five decision slots and return ``[{id, district}, ...]`` and cost."""
    names = {item["id"]: f'{item["id"]} — {item["name"]} ({item["cost"]} у.е.)' for item in initiatives}
    by_label = {label: initiative_id for initiative_id, label in names.items()}
    by_id = {item["id"]: item for item in initiatives}
    district_names = [item["name"] for item in districts]
    all_ids = list(names)

    st.subheader("Выберите пять мероприятий")
    decisions = []
    total_cost = 0
    for slot in range(5):
        key = f"decision_{slot}_label"
        current_label = st.session_state.get(key, names[all_ids[slot % len(all_ids)]])
        previous_id = by_label.get(current_label, all_ids[slot % len(all_ids)])
        previous_type = st.session_state.get(f"decision_{slot}_type")
        current_type = by_id[previous_id]["type"]
        district_key = f"decision_{slot}_district"
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

    st.sidebar.metric("Стоимость решений", f"{total_cost} у.е.")
    st.sidebar.metric("Остаток бюджета", f"{100 - total_cost} у.е.")
    st.sidebar.caption(f"Выбрано позиций: {len(decisions)} из 5")
    if total_cost > 100:
        st.sidebar.error("Превышен виртуальный бюджет в 100 у.е.")
    return decisions, total_cost
