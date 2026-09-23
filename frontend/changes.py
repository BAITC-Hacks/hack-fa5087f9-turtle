"""Streamlit-блок с изменениями районов и активными синергиями."""

import streamlit as st


INDICATOR_LABELS = {
    "T1": "Разгрузка дорог",
    "T2": "Доступность общественного транспорта",
    "E1": "Озеленение",
    "E2": "Качество воздуха",
    "S1": "Школы и детские сады",
    "S2": "Поликлиники и первичная помощь",
    "B1": "Безопасность улиц",
    "B2": "Безопасность дорожного движения",
    "C1": "Надёжность ЖКХ",
    "C2": "Скорость решения обращений",
}


def render_changes(changes: list[dict], synergies: list[dict]) -> None:
    """Показывает таблицу до/после для района и список синергий."""
    st.subheader("Изменения показателей районов")
    if not changes:
        st.info("Изменений показателей нет.")
    else:
        district_names = list(dict.fromkeys(row["district"] for row in changes))
        selected_district = st.selectbox(
            "Район для просмотра",
            district_names,
            key="changes_district",
        )
        district_rows = []
        critical_indicators = []
        for row in changes:
            if row["district"] != selected_district:
                continue
            indicator = row["indicator"]
            is_critical = bool(row.get("critical", row["after"] < 40))
            district_rows.append(
                {
                    "Показатель": f"{indicator} — {INDICATOR_LABELS.get(indicator, indicator)}",
                    "До": round(row["before"], 2),
                    "После": round(row["after"], 2),
                    "Изменение": round(row["delta"], 2),
                    "Статус": "Критично (<40)" if is_critical else "Норма",
                }
            )
            if is_critical:
                critical_indicators.append(indicator)

        st.dataframe(district_rows, use_container_width=True, hide_index=True)
        if critical_indicators:
            st.warning(
                "Критические показатели района: "
                + ", ".join(critical_indicators)
                + ". Значение 40 критическим не считается."
            )

    st.subheader("Сработавшие синергии")
    if not synergies:
        st.write("Синергии в выбранном наборе не сработали.")
        return

    synergy_rows = []
    for synergy in synergies:
        first_id, second_id = synergy["pair"]
        district = synergy.get("district") or "весь город"
        effects = synergy.get("effect")
        if effects is None:
            effects = {synergy["indicator"]: synergy["bonus"]}
        for indicator, bonus in effects.items():
            synergy_rows.append(
                {
                    "Пара": f"{first_id} + {second_id}",
                    "Район": district,
                    "Показатель": f"{indicator} — {INDICATOR_LABELS.get(indicator, indicator)}",
                    "Бонус": f"+{bonus}",
                }
            )
    st.dataframe(synergy_rows, use_container_width=True, hide_index=True)
