"""
Интерфейс: выбор 5 решений, бюджет-трекер, кнопка расчёта, показ результата + объяснения.
Владелец фичи: [впишите имя]

Streamlit выбран для скорости (один файл, без отдельного фронт/бэк деплоя).
Запуск: streamlit run frontend/app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.scoring import load_data, run  # noqa: E402
from ai.explain import explain_result  # noqa: E402

st.set_page_config(page_title="Аким на 5 часов", layout="wide")
st.title("Аким на 5 часов -- AI-симулятор управления городом")

districts, initiatives, rules = load_data()

st.sidebar.header(f"Бюджет: {rules['budget']} у.е.")
# TODO: собрать выбор 5 мероприятий (с районом для типа "Район")
# TODO: живой счётчик потраченного бюджета в sidebar
# TODO: кнопка "Рассчитать" -> вызвать run(decisions) -> показать score + объяснение explain_result(...)
# TODO: если невалидно -- показать причину (result["reason"]), не пытаться считать score

st.info("Каркас интерфейса. Реализуйте выбор решений и вывод результата.")
