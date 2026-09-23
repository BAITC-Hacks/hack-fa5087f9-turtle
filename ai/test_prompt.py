import unittest

from ai.prompt import SYSTEM_PROMPT, build_user_prompt


class PromptTests(unittest.TestCase):
    def test_system_prompt_requires_grounded_three_part_answer(self):
        self.assertIn("Что улучшилось", SYSTEM_PROMPT)
        self.assertIn("Какие проблемы остались", SYSTEM_PROMPT)
        self.assertIn("Какие компромиссы", SYSTEM_PROMPT)
        self.assertIn("Не вычисляй новые значения", SYSTEM_PROMPT)
        self.assertIn("не выдавай симуляцию за точный прогноз", SYSTEM_PROMPT)
        self.assertIn("score_delta — изменение итогового Score", SYSTEM_PROMPT)
        self.assertIn("Не называй score_delta изменением среднего балла города", SYSTEM_PROMPT)
        self.assertIn("Не вычитай значения", SYSTEM_PROMPT)
        self.assertIn("из base_result", SYSTEM_PROMPT)
        self.assertIn("только из поля changes", SYSTEM_PROMPT)

    def test_user_prompt_preserves_context_facts(self):
        context = {
            "score": 56.54307,
            "score_delta": 3.98539,
            "d_avg": 58.08,
            "min_district": "Нура",
            "synergies": [
                {
                    "pair": ["M10", "M12"],
                    "district": "Нура",
                    "indicator": "B1",
                    "bonus": 2,
                }
            ],
        }

        prompt = build_user_prompt(context)

        self.assertIn("56.54307", prompt)
        self.assertIn("3.98539", prompt)
        self.assertIn("58.08", prompt)
        self.assertIn("Нура", prompt)
        self.assertIn('"M10"', prompt)
        self.assertIn('"M12"', prompt)
        self.assertIn('"bonus": 2', prompt)


if __name__ == "__main__":
    unittest.main()
