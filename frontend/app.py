"""Streamlit entry point for «Аким на 5 часов»."""

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from ai.context import build_context  # noqa: E402
from ai.explain import available_models, explain_result  # noqa: E402
from engine.changes import describe_changes  # noqa: E402
from engine.scoring import load_data, run, validate_decisions  # noqa: E402
from frontend.changes import render_changes  # noqa: E402
from frontend.result import render_result  # noqa: E402
from frontend.selection import render_selection  # noqa: E402
from frontend.theme import apply_theme  # noqa: E402


st.set_page_config(
    page_title="Аким на 5 часов · городской симулятор",
    page_icon=str(Path(__file__).with_name("favicon.svg")),
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()

district_source, initiatives, rules = load_data()
if isinstance(district_source, dict):
    districts = district_source["districts"]
    profiles = district_source.get("profiles", {})
else:
    districts = district_source
    source_file = Path(__file__).parent.parent / "data" / "districts.json"
    profiles = json.loads(source_file.read_text(encoding="utf-8")).get("profiles", {})

decisions, _total_cost = render_selection(
    initiatives, districts, rules, profiles=profiles
)
signature = tuple((item["id"], item.get("district")) for item in decisions)

# A changed scenario must never keep showing a result or explanation for old choices.
if st.session_state.get("calculated_signature") != signature:
    for key in ("calculation", "explanation", "ai_context", "explanation_settings"):
        st.session_state.pop(key, None)

is_valid, validation_reason = validate_decisions(decisions, initiatives, rules)
st.markdown(
    '<div class="section-label">03 · Проверка и расчёт</div>',
    unsafe_allow_html=True,
)
if not is_valid:
    st.error(validation_reason, icon="⚠️")

if st.button("Рассчитать сценарий", type="primary", use_container_width=True):
    if is_valid:
        result = run(decisions)
        st.session_state["calculated_signature"] = signature
        st.session_state["calculation"] = result
        st.session_state.pop("explanation", None)
        st.session_state.pop("ai_context", None)
        st.session_state.pop("explanation_settings", None)
    else:
        st.error(validation_reason, icon="⚠️")

result = st.session_state.get("calculation")
if result is None:
    st.info("Контрольный набор из задания уже загружен. Измените решения или рассчитайте его результат.")
elif not result.get("valid", False):
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

    st.markdown(
        '<div class="section-label">04 · Результат сценария</div>',
        unsafe_allow_html=True,
    )
    render_result(result)

    if display_result.get("changes") is not None:
        if "changes_district" not in st.session_state:
            st.session_state["changes_district"] = result.get("min_district")
        with st.expander("Показатели до/после и сработавшие синергии", expanded=True):
            render_changes(display_result["changes"], display_result.get("synergies", []))
    else:
        st.info("Движок пока не передал детализацию изменений районов.")

    st.markdown('<div class="section-label">05 · Объяснение</div>', unsafe_allow_html=True)
    st.markdown("### AI объясняет рассчитанный результат")
    st.caption("Числа рассчитывает движок; модель объясняет уже готовые эффекты, бюджет, лаги и компромиссы.")
    models = available_models()
    with st.expander("Настройки объяснения", expanded=False):
        selected_model = st.selectbox("Модель AI", models, key="ai_model")
        offline = st.checkbox(
            "Показать работу без AI",
            key="offline_demo",
            help="Запрос к API не отправляется. Можно проверить резервное объяснение.",
        )
    settings = (selected_model, offline)
    if st.session_state.get("explanation_settings") != settings:
        st.session_state.pop("explanation", None)
    if st.button("Получить AI-объяснение", use_container_width=True):
        st.session_state["ai_context"] = context
        with st.spinner("Подготавливаем объяснение по рассчитанному сценарию…"):
            st.session_state["explanation"] = explain_result(
                context,
                decisions,
                model=selected_model,
                offline=offline,
            )
            st.session_state["explanation_settings"] = settings
    if st.session_state.get("explanation"):
        if st.session_state["explanation"].startswith("Резервное объяснение без AI"):
            st.info("Резервное объяснение без AI. Расчёт и таблицы остаются доступными.")
        else:
            st.caption(f"AI-комментарий: {selected_model}. Числовые факты взяты из расчёта движка.")
        with st.container(border=True, key="ai_explanation"):
            st.markdown(st.session_state["explanation"])
    with st.expander("Проверить факты, переданные AI", expanded=False):
        st.json(context, expanded=False)

st.markdown(
    '<footer class="app-footer">Учебная симуляция · Числа рассчитывает движок, '
    'AI объясняет результат · Astana Innovations / HackAlem AI</footer>',
    unsafe_allow_html=True,
)
