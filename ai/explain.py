"""
AI-объяснение результата. Владелец фичи: Томирис.

Роль ИИ по ТЗ: получает УЖЕ ПОСЧИТАННЫЙ результат (дельты по районам/показателям,
вклад каждой меры) и объясняет его человеку. AI НЕ считает числа сам и не придумывает их.
"""

import os
from pathlib import Path

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)
from ai.prompt import SYSTEM_PROMPT, build_user_prompt
from ai.response import RESPONSE_FORMAT, number, render_response, synergy_texts

MODEL = "gpt-4o-mini"
ENV_FILE = Path(__file__).parent.parent / ".env"

FALLBACK_TEXT = (
    "Резервное объяснение без AI: подробности сценария сейчас недоступны. "
    "Посчитанные показатели выше остаются результатом движка."
)


def _load_local_env() -> None:
    """Load the two supported settings from an ignored local .env file."""
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name not in {"OPENAI_API_KEY", "OPENAI_MODEL"}:
            continue
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(name, value)


def _fallback_explanation(context: dict, api_status: str | None = None) -> str:
    """Describe only values already present in the engine context."""
    result = context.get("result") or context
    score = context.get("score", result.get("score"))
    score_delta = context.get("score_delta", result.get("score_delta"))
    n_crit = context.get("n_crit", result.get("n_crit"))
    lines = ["Резервное объяснение без AI."]
    if api_status:
        lines.append(api_status)

    if isinstance(score, (int, float)):
        score_line = f"Итоговый Astana Quality of Life Score: {score:.2f}"
        if isinstance(score_delta, (int, float)):
            score_line += f" ({score_delta:+.2f} к базовому сценарию)"
        lines.append(score_line + ".")

    improvements = [
        change for change in (context.get("changes") or [])
        if isinstance(change.get("delta"), (int, float)) and change["delta"] > 0
    ]
    improvements.sort(key=lambda change: change["delta"], reverse=True)
    if improvements:
        highlights = [
            f'{change["district"]}: {change["indicator"]} +{number(change["delta"])}'
            for change in improvements[:3]
        ]
        lines.append("Наибольшие улучшения по данным движка: " + "; ".join(highlights) + ".")

    critical_values = context.get("critical_values", result.get("critical_values"))
    if critical_values:
        critical = [
            f'{item["district"]}: {item["indicator"]}={item["value"]:g}'
            for item in critical_values[:3]
        ]
        lines.append("Оставшиеся критические значения: " + "; ".join(critical) + ".")
    elif isinstance(n_crit, int):
        lines.append(f"Показателей ниже критического порога: {n_crit}.")

    decisions = context.get("decisions", [])
    if decisions:
        names = [item.get("name", item.get("id", "мероприятие")) for item in decisions]
        total_cost = context.get("total_cost")
        budget = context.get("budget")
        choice_line = "Выбранные меры: " + ", ".join(names)
        if isinstance(total_cost, (int, float)) and isinstance(budget, (int, float)):
            choice_line += f"; стоимость {total_cost:g} из {budget:g} у.е."
        lines.append(choice_line + ".")

    synergies = context.get("synergies") or []
    if synergies:
        details = synergy_texts(context)
        if details:
            lines.append("Сработавшие синергии: " + "; ".join(details) + ".")
    else:
        lines.append("Синергии в выбранном наборе не сработали.")

    if context.get("changes") is None:
        lines.append("Детализация изменений районов движком не передана.")
    return " ".join(lines) if len(lines) > 1 else FALLBACK_TEXT


def configured_model() -> str:
    _load_local_env()
    return os.getenv("OPENAI_MODEL", MODEL)


def explain_result(engine_result: dict, decisions: list[dict], *, model: str | None = None, offline: bool = False) -> str:
    """
    engine_result: результат engine.scoring.run() (score, district_scores, n_crit, ...)
    decisions: выбранные решения
    Возвращает текстовое объяснение для пользователя.
    """
    if not engine_result.get("valid", True):
        return f"Набор решений не прошёл проверку: {engine_result.get('reason', 'причина не указана')}"

    context = engine_result
    if "decisions" not in context:
        context = {**engine_result, "decisions": decisions}
    if offline:
        return _fallback_explanation(context, "Включён демонстрационный режим без AI.")
    _load_local_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_explanation(
            context,
            "Ключ OpenAI не найден. Добавьте OPENAI_API_KEY в локальный файл .env.",
        )

    try:
        client = OpenAI(api_key=api_key, timeout=20.0, max_retries=0)
        response = client.chat.completions.create(
            model=model or configured_model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(context)},
            ],
            temperature=0.3,
            response_format=RESPONSE_FORMAT,
            max_completion_tokens=900,
        )
        content = response.choices[0].message.content
        if response.choices[0].finish_reason != "stop" or not content:
            return _fallback_explanation(context, "AI не вернул полное объяснение.")
        try:
            return render_response(content, context)
        except (ValueError, TypeError):
            return _fallback_explanation(context, "Ответ AI не прошёл проверку формата или фактов. Повторите запрос.")
    except AuthenticationError:
        return _fallback_explanation(
            context,
            "OpenAI отклонил ключ. Проверьте значение OPENAI_API_KEY в файле .env.",
        )
    except PermissionDeniedError:
        return _fallback_explanation(
            context,
            "У проекта этого ключа нет доступа к выбранной модели OpenAI.",
        )
    except RateLimitError:
        return _fallback_explanation(
            context,
            "OpenAI сообщил об ограничении запросов или доступного баланса API.",
        )
    except (APIConnectionError, APITimeoutError):
        return _fallback_explanation(
            context,
            "Не удалось подключиться к OpenAI. Проверьте интернет и повторите запрос.",
        )
    except BadRequestError:
        return _fallback_explanation(
            context,
            "OpenAI не принял запрос или указанную в OPENAI_MODEL модель.",
        )
    except Exception:
        return _fallback_explanation(
            context,
            "AI-запрос завершился с ошибкой; расчёт движка остаётся действительным.",
        )
