"""Панель результата расчёта. Владелец фичи: Томирис."""

import streamlit as st


def render_result(result: dict) -> None:
    """Display engine values without recalculating or modifying them."""
    st.subheader("Итог сценария")
    score = result.get("score")
    score_delta = result.get("score_delta")
    score_col, col1, col2, col3 = st.columns([1.5, 1, 1, 1])
    if score is not None:
        delta_text = f"{score_delta:+.2f} к базе" if score_delta is not None else None
        score_col.metric(
            "Astana Quality of Life Score",
            f"{score:.2f}",
            delta=delta_text,
        )

    if result.get("d_avg") is not None:
        col1.metric("Средний балл города", f"{result['d_avg']:.2f}")
    if result.get("min_district") is not None:
        col2.metric("Слабейший район", result["min_district"])
    if result.get("n_crit") is not None:
        col3.metric("Критические значения", result["n_crit"])

    district_scores = result.get("district_scores", {})
    if district_scores:
        st.subheader("Баллы районов")
        st.dataframe(
            [
                {"Район": district, "Балл": round(value, 2)}
                for district, value in district_scores.items()
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Балл": st.column_config.ProgressColumn(
                    "Балл / 100", min_value=0, max_value=100, format="%.2f"
                )
            },
        )
