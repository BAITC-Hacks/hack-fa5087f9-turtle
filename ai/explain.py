"""
AI-объяснение результата. Владелец фичи: [впишите имя]

Роль ИИ по ТЗ: получает УЖЕ ПОСЧИТАННЫЙ результат (дельты по районам/показателям,
вклад каждой меры) и объясняет его человеку. AI НЕ считает числа сам и не придумывает их.
"""

import json
import os

from openai import OpenAI, OpenAIError

SYSTEM_PROMPT = """Ты помогаешь объяснить результат симуляции городского бюджета.
Тебе дают уже посчитанные цифры (score, изменения по районам и показателям, какие меры выбраны).
Никогда не придумывай и не пересчитывай числа -- только интерпретируй то, что дано.
Объясни: (1) сильные стороны сценария, (2) риски/компромиссы, (3) что осталось нерешённым.
Пиши кратко, понятно для человека без технического бэкграунда, на русском."""

MODEL = "gpt-4o-mini"

FALLBACK_TEXT = (
    "AI-объяснение сейчас недоступно (ошибка обращения к OpenAI API). "
    "Посчитанные цифры выше верны и не зависят от этого шага -- попробуйте "
    "нажать «Получить AI-объяснение» ещё раз."
)


def explain_result(engine_result: dict, decisions: list[dict]) -> str:
    """
    engine_result: результат engine.scoring.run() (score, district_scores, n_crit, ...)
    decisions: выбранные решения
    Возвращает текстовое объяснение для пользователя.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user_prompt = (
        "Результат расчёта (JSON):\n"
        f"{json.dumps(engine_result, ensure_ascii=False, default=str)}\n\n"
        "Выбранные решения (JSON):\n"
        f"{json.dumps(decisions, ensure_ascii=False, default=str)}"
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except OpenAIError:
        return FALLBACK_TEXT
