"""Verify the project and start the demo with the same Python interpreter."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверить проект и запустить демо")
    parser.add_argument("--check-only", action="store_true", help="Проверить без запуска веб-сервера")
    parser.add_argument("--live-ai", action="store_true", help="Дополнительно отправить один платный запрос в OpenAI")
    parser.add_argument("--model", help="Модель для дополнительной проверки AI")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Порт должен быть в диапазоне 1–65535")

    print("Проверяем проект…", flush=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    if tests.returncode:
        print("Проверки не прошли. Исправьте ошибки выше перед демонстрацией.")
        return tests.returncode

    from engine.scoring import load_data, run
    from ai.context import build_context
    from ai.explain import configured_model, explain_result
    from ai.response import synergy_texts

    _, _, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    result = run(decisions)
    if not result.get("valid"):
        print("Контрольный набор не прошёл валидацию:", result.get("reason"))
        return 1
    context = build_context(decisions, result)
    print(f'Контроль: стоимость {context["total_cost"]}; Score {result["score"]:.2f}; критических значений {result["n_crit"]}.')
    for synergy in synergy_texts(context):
        print("Синергия:", synergy)

    ai_failed = False
    if args.live_ai:
        model = args.model or configured_model()
        print(f"Проверяем живой AI: {model}…", flush=True)
        answer = explain_result(context, decisions, model=model)
        ai_failed = answer.startswith("Резервное объяснение без AI")
        print("РЕЗЕРВНЫЙ ОТВЕТ" if ai_failed else "ЖИВОЙ AI — ответ получен")
        print(answer)
        if ai_failed:
            print("AI не подтверждён. Приложение доступно с резервным объяснением.")
    else:
        print("Живой API не проверялся. Для проверки добавьте --live-ai.")

    if args.check_only:
        return int(ai_failed)

    print(f"Открывайте http://localhost:{args.port}. Остановка: Ctrl+C.", flush=True)
    try:
        return subprocess.call([
            sys.executable, "-m", "streamlit", "run", str(ROOT / "frontend/app.py"),
            "--server.port", str(args.port),
        ], cwd=ROOT)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
