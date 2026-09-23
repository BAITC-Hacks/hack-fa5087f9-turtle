"""Streamlit entry point for «Аким на 5 часов»."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from ai.context import build_context  # noqa: E402
from ai.explain import explain_result  # noqa: E402
from engine.changes import describe_changes  # noqa: E402
from engine.scoring import load_data, run  # noqa: E402
from frontend.changes import render_changes  # noqa: E402
from frontend.selection import render_selection  # noqa: E402


st.set_page_config(page_title="Аким на 5 часов", layout="wide")
st.title("Аким на 5 часов — AI-симулятор управления городом")
st.caption("Распределите общий виртуальный бюджет 100 у.е. между пятью решениями.")

district_data, initiatives, rules = load_data()
districts = district_data["districts"] if isinstance(district_data, dict) else district_data
decisions, total_cost = render_selection(initiatives, districts, rules)
signature = tuple((item["id"], item.get("district")) for item in decisions)

if st.session_state.get("calculated_signature") != signature:
    st.session_state.pop("calculation", None)
    st.session_state.pop("explanation", None)

if st.button("Рассчитать сценарий", type="primary"):
    if total_cost > rules["budget"]:
        st.error(f"Превышен бюджет: {total_cost} из {rules['budget']} у.е.")
        st.session_state.pop("calculation", None)
        st.session_state.pop("explanation", None)
    else:
        result = run(decisions)
        st.session_state["calculated_signature"] = signature
        st.session_state["calculation"] = result
        st.session_state.pop("explanation", None)

result = st.session_state.get("calculation")
if result:
    if not result.get("valid", False):
        st.error(result.get("reason", "Набор решений не прошёл проверку."))
    else:
        display_result = result
        if result.get("before") is not None and result.get("after") is not None:
            change_summary = describe_changes(result["before"], result["after"], decisions, rules)
            display_result = {
                **result,
                "changes": result.get("changes") or change_summary["changes"],
                "synergies": result.get("synergies") or change_summary["synergies"],
            }
        context = build_context(decisions, display_result, initiatives, districts, rules)
        st.subheader("Итог сценария")
        score = result.get("score")
        score_delta = result.get("score_delta")
        if score is not None:
            delta_text = f"{score_delta:+.2f} к базе" if score_delta is not None else None
            st.metric(
                "Astana Quality of Life Score",
                f"{score:.2f}",
                delta=delta_text,
            )

        col1, col2, col3 = st.columns(3)
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
            )

        if display_result.get("changes") is not None:
            render_changes(display_result["changes"], display_result.get("synergies", []))
        else:
            st.info("Движок пока не передал детализацию изменений районов.")

        if st.button("Получить AI-объяснение"):
            st.session_state["ai_context"] = context
            with st.spinner("Подготавливаем объяснение…"):
                st.session_state["explanation"] = explain_result(context, decisions)
        if st.session_state.get("explanation"):
            st.subheader("Объяснение сценария")
            st.write(st.session_state["explanation"])
else:
    st.info("Выберите пять решений и нажмите «Рассчитать сценарий».")
