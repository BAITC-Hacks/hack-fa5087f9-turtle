"""Opt-in live comparison. Run from the repository root; never logs the API key."""

import argparse
from time import monotonic

from ai.context import build_context
from ai.explain import explain_result
from engine.scoring import load_data, run


def main():
    parser = argparse.ArgumentParser(description="Проверка живых AI-ответов на контрольном сценарии")
    parser.add_argument("--models", nargs="+", default=["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"])
    args = parser.parse_args()
    _, _, rules = load_data()
    decisions = rules["known_results"]["example_valid_set"]["decisions"]
    context = build_context(decisions, run(decisions))
    failed = False
    for model in args.models:
        start = monotonic()
        answer = explain_result(context, decisions, model=model)
        fallback = answer.startswith("Резервное объяснение без AI")
        failed |= fallback
        print(f"\n{model}: {'РЕЗЕРВНЫЙ ОТВЕТ' if fallback else 'ЖИВОЙ AI'}, {monotonic() - start:.2f} с")
        print(answer)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
