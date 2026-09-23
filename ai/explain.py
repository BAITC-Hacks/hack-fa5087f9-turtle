"""
AI-объяснение результата. Владелец фичи: [впишите имя]

Роль ИИ по ТЗ: получает УЖЕ ПОСЧИТАННЫЙ результат (дельты по районам/показателям,
вклад каждой меры) и объясняет его человеку. AI НЕ считает числа сам и не придумывает их.
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """Ты помогаешь объяснить результат симуляции городского бюджета.
Тебе дают уже посчитанные цифры (score, изменения по районам и показателям, какие меры выбраны).
Никогда не придумывай и не пересчитывай числа -- только интерпретируй то, что дано.
Объясни: (1) сильные стороны сценария, (2) риски/компромиссы, (3) что осталось нерешённым.
Пиши кратко, понятно для человека без технического бэкграунда, на русском."""


def explain_result(engine_result: dict, decisions: list[dict]) -> str:
    """
    engine_result: результат engine.scoring.run() (score, district_scores, n_crit, ...)
    decisions: выбранные решения
    Возвращает текстовое объяснение для пользователя.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user_prompt = f"Результат расчёта: {engine_result}\nВыбранные решения: {decisions}"
    # TODO: вызвать client.chat.completions.create(...) с SYSTEM_PROMPT + user_prompt
    # TODO: обработать ошибку API (таймаут / rate limit) -- вернуть fallback-текст
    raise NotImplementedError
