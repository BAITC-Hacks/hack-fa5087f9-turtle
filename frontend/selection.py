"""District dataset and five-slot decision interface for the simulator."""

from __future__ import annotations

from html import escape

import streamlit as st
from engine.scoring import validate_decisions


INDICATOR_LABELS = {
    "T1": "Разгрузка дорог",
    "T2": "Доступность общественного транспорта",
    "E1": "Озеленение",
    "E2": "Качество воздуха",
    "S1": "Школы и детсады",
    "S2": "Поликлиники и первичная медпомощь",
    "B1": "Безопасность улиц",
    "B2": "Безопасность дорожного движения",
    "C1": "Надёжность ЖКХ",
    "C2": "Скорость решения обращений жителей",
}


def render_district_overview(
    districts: list[dict],
    rules: dict,
    profiles: dict[str, str] | None = None,
) -> None:
    """Show the actual baseline district data and the full indicator table."""
    profiles = profiles or {}
    weights = rules.get("weights", {})
    threshold = rules.get("critical_threshold", 40)

    st.markdown('<div class="section-label">01 · Исходные данные</div>', unsafe_allow_html=True)
    st.markdown("### Пять районов города")
    st.markdown(
        '<p class="section-intro">Это одинаковый для всех команд синтетический набор, '
        'а не реальные оперативные данные города. Карточки показывают долю населения, '
        'профиль района и показатели ниже критического порога '
        f'{threshold}.</p>',
        unsafe_allow_html=True,
    )

    columns = st.columns(len(districts), gap="small") if districts else []
    for index, (column, district) in enumerate(zip(columns, districts)):
        signals = [
            (code, district.get(code))
            for code in weights
            if district.get(code) is not None and district[code] < threshold
        ]
        chips = "".join(
            '<span class="district-chip">'
            f'{escape(code)} · {escape(INDICATOR_LABELS.get(code, code))} '
            f'{value:g}</span>'
            for code, value in signals
        )
        if not chips:
            chips = '<span class="district-calm">Нет стартовых значений ниже порога</span>'
        name = escape(str(district.get("name", "Район")))
        profile = escape(str(profiles.get(district.get("name"), "")))
        pop_share = district.get("pop_share", 0)
        population = f"{pop_share:.0%} жителей" if isinstance(pop_share, (int, float)) else ""
        with column:
            st.markdown(
                f"""
                <article class="district-card" style="animation-delay:{index * 0.07:.2f}s">
                  <div class="district-card-head">
                    <span class="district-card-name">{name}</span>
                    <span class="district-card-pop">{escape(population)}</span>
                  </div>
                  <p class="district-card-profile">{profile}</p>
                  <div class="district-signals-label">На старте · ниже {threshold}</div>
                  <div class="district-chips">{chips}</div>
                </article>
                """,
                unsafe_allow_html=True,
            )

    indicator_codes = list(weights)
    with st.expander("Открыть полный исходный набор показателей", expanded=False):
        st.caption(
            "Значения 0–100 взяты из data/districts.json; большее значение означает "
            "лучший результат. Доля населения используется движком при расчёте среднего балла города."
        )
        table = []
        for district in districts:
            row = {
                "Район": district.get("name"),
                "Доля населения": f"{district['pop_share']:.0%}",
                "Профиль": profiles.get(district.get("name"), ""),
            }
            row.update(
                {
                    f"{code} · {INDICATOR_LABELS.get(code, code)}": district.get(code)
                    for code in indicator_codes
                }
            )
            table.append(row)
        st.table(table)


def _default_decisions(initiatives: list[dict], rules: dict, districts: list[dict]) -> list[dict]:
    """Prefer the checked example stored in rules.json; never duplicate catalog data here."""
    count = rules.get("num_decisions", 5)
    by_id = {initiative.get("id"): initiative for initiative in initiatives}
    district_names = [district.get("name") for district in districts]
    sample = rules.get("known_results", {}).get("example_valid_set", {}).get("decisions", [])
    if len(sample) == count and all(item.get("id") in by_id for item in sample):
        return [{"id": item["id"], "district": item.get("district")} for item in sample]

    defaults = []
    for initiative in initiatives[:count]:
        defaults.append(
            {
                "id": initiative["id"],
                "district": district_names[0] if initiative.get("type") == "Район" and district_names else None,
            }
        )
    return defaults


def _render_budget_summary(total_cost: int | float, budget: int | float, count: int, required: int) -> None:
    remaining = budget - total_cost
    percentage = max(0, min(100, 100 * total_cost / budget if budget else 0))
    over_budget = total_cost > budget
    over_class = " is-over" if over_budget else ""
    status_class = "budget-status is-over" if over_budget else "budget-status"
    status = f"Превышение на {total_cost - budget:g} у.е." if over_budget else "В пределах бюджета"
    fill_width = f"{percentage:.2f}%"
    cost_col, rest_col, count_col = st.columns(3, gap="small")
    cost_col.metric("Стоимость решений", f"{total_cost:g} у.е.")
    rest_col.metric("Остаток бюджета", f"{remaining:g} у.е.")
    count_col.metric("Выбрано позиций", f"{count} из {required}")
    st.markdown(
        f"""
        <div class="budget-status-row"><span class="{status_class}">{status}</span>
          <span class="budget-explainer">Единый виртуальный бюджет · не тенге</span></div>
        <div class="budget-track" role="progressbar" aria-label="Использовано виртуального бюджета"
             aria-valuemin="0" aria-valuemax="{budget}" aria-valuenow="{max(0, min(budget, total_cost))}">
          <span class="budget-fill{over_class}" style="width:{fill_width}"></span>
        </div>
        <div class="budget-foot"><span>Лимит: {budget:g} у.е.</span><span>Остаток не даёт бонуса</span></div>
        """,
        unsafe_allow_html=True,
    )


def render_selection(
    initiatives: list[dict],
    districts: list[dict],
    rules: dict,
    profiles: dict[str, str] | None = None,
) -> tuple[list[dict], int]:
    """Render the source dataset and decision slots; return decisions and cost."""
    render_district_overview(districts, rules, profiles)

    st.markdown('<div class="section-label">02 · Сборка сценария</div>', unsafe_allow_html=True)
    st.markdown("### Распределите бюджет")
    st.markdown(
        '<p class="section-intro">Выберите ровно пять разных мероприятий. '
        'Для районной меры выберите район; городская автоматически охватывает все районы. '
        f'Показан полный эффект меры до лага; движок учитывает срок начала действия '
        f'на горизонте {rules.get("horizon_quarters", 8)} кварталов.</p>',
        unsafe_allow_html=True,
    )

    by_id = {item["id"]: item for item in initiatives}
    initiative_ids = list(by_id)
    district_names = [item["name"] for item in districts]
    decision_count = rules.get("num_decisions", 5)
    defaults = _default_decisions(initiatives, rules, districts)
    if len(defaults) < decision_count:
        st.error("В каталоге меньше мероприятий, чем требует игровой сценарий.")
        return [], 0

    decisions: list[dict] = []
    total_cost: int | float = 0
    for slot in range(decision_count):
        default = defaults[slot]
        default_id = default["id"]
        if default_id not in by_id:
            default_id = initiative_ids[slot % len(initiative_ids)]

        label_key = f"decision_{slot}_label"
        labels_by_id = {
            item_id: f"{item_id} — {by_id[item_id]['name']}"
            for item_id in initiative_ids
        }
        ids_by_label = {label: item_id for item_id, label in labels_by_id.items()}
        if label_key not in st.session_state:
            old_id = st.session_state.pop(f"decision_{slot}_id", None)
            old_label = st.session_state.pop(label_key, None)
            if old_label:
                old_id = str(old_label).split(" — ", 1)[0]
            selected_id = old_id if old_id in by_id else default_id
            st.session_state[label_key] = labels_by_id[selected_id]
        elif st.session_state[label_key] not in ids_by_label:
            old_id = str(st.session_state[label_key]).split(" — ", 1)[0]
            old_id = old_id if old_id in by_id else default_id
            st.session_state[label_key] = labels_by_id[old_id]

        selected_label = st.session_state[label_key]
        selected_id = ids_by_label[selected_label]
        initiative = by_id[selected_id]

        district_key = f"decision_{slot}_district"
        type_key = f"decision_{slot}_type"
        previous_type = st.session_state.get(type_key)
        if previous_type != initiative["type"] and initiative["type"] == "Город":
            st.session_state.pop(district_key, None)
        if initiative["type"] == "Район" and district_names:
            if st.session_state.get(district_key) not in district_names:
                default_district = default.get("district")
                st.session_state[district_key] = (
                    default_district if default_district in district_names else district_names[0]
                )

        with st.container(border=True):
            left, middle, right = st.columns([5.4, 3.1, 1.1], gap="medium")
            with left:
                selected_label = st.selectbox(
                    f"Мероприятие · {slot + 1:02d}",
                    options=list(ids_by_label),
                    key=label_key,
                )
                selected_id = ids_by_label[selected_label]
                initiative = by_id[selected_id]
            with middle:
                if initiative.get("type") == "Район":
                    if district_names:
                        district = st.selectbox(
                            f"Район · {slot + 1:02d}",
                            options=district_names,
                            key=district_key,
                            help="Эффект районного мероприятия применяется только здесь.",
                        )
                    else:
                        district = None
                        st.error("Нет загруженных районов.")
                else:
                    district = None
                    st.markdown(
                        '<div class="coverage-pill"><span class="coverage-dot"></span>'
                        'Весь город · все районы</div>',
                        unsafe_allow_html=True,
                    )
            with right:
                st.markdown(
                    '<div class="initiative-price"><span>Стоимость</span>'
                    f'<strong>{initiative["cost"]}</strong><span>у.е.</span></div>',
                    unsafe_allow_html=True,
                )

            st.session_state[type_key] = initiative.get("type")
            effect_summary = " · ".join(
                f"{INDICATOR_LABELS.get(code, code)} {value:+g}"
                for code, value in initiative.get("effects", {}).items()
            )
            st.markdown(
                '<div class="decision-meta">'
                f'<span class="meta-pill">{escape(str(initiative.get("direction", "")))}</span>'
                f'<span>Эффект до учёта срока: {escape(effect_summary)}</span>'
                f'<span>Начало эффекта через {initiative.get("lag", "?")} кв.</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        decisions.append({"id": initiative["id"], "district": district})
        total_cost += initiative["cost"]

    budget = rules.get("budget", 100)
    _render_budget_summary(total_cost, budget, len(decisions), decision_count)
    valid, _reason = validate_decisions(decisions, initiatives, rules)
    if valid:
        st.success("Набор подходит под правила симуляции. Можно рассчитать сценарий.", icon="✅")
    return decisions, total_cost
