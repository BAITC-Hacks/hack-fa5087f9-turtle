"""Exercise actual Streamlit widgets, including failed and successful API calls."""

from pathlib import Path
from unittest.mock import Mock

try:
    import httpx2 as httpx  # OpenAI SDK 3.x
except ImportError:
    import httpx  # OpenAI SDK 1.x/2.x
import pytest
from openai import APITimeoutError
from streamlit.testing.v1 import AppTest

from ai import explain
from ai.test_explain import completion_response

APP = Path(__file__).with_name("app.py")


def click(app, label):
    next(button for button in app.button if button.label == label).click().run()
    assert not app.exception


def metrics(app):
    return {metric.label: metric.value for metric in app.metric}


@pytest.mark.parametrize("failure", ["missing_key", "timeout", "offline_demo"])
def test_fallback_keeps_score_and_all_three_tables(monkeypatch, tmp_path, failure):
    monkeypatch.setattr(explain, "ENV_FILE", tmp_path / "absent.env")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = Mock()
    client.chat.completions.create.side_effect = APITimeoutError(request=httpx.Request("POST", "https://api.openai.com"))
    factory = Mock(return_value=client)
    monkeypatch.setattr(explain, "OpenAI", factory)
    if failure != "missing_key":
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    app = AppTest.from_file(str(APP)).run()
    click(app, "Рассчитать сценарий")
    before_tables = [frame.value.copy() for frame in app.dataframe]
    before_metrics = metrics(app)
    if failure == "offline_demo":
        app.checkbox(key="offline_demo").check().run()
    click(app, "Получить AI-объяснение")
    assert metrics(app) == before_metrics
    assert metrics(app)["Astana Quality of Life Score"] == "56.54"
    assert metrics(app)["Стоимость решений"] == "95 у.е."
    assert len(before_tables) == len(app.dataframe) == 3
    for old, current in zip(before_tables, app.dataframe):
        assert old.equals(current.value)
    assert any("Резервное объяснение без AI" in info.value for info in app.info)
    answer = app.session_state["explanation"]
    assert "M10 + M12 в районе Нура: B1 +2" in answer
    if failure != "timeout":
        factory.assert_not_called()


def test_live_answer_and_selection_change_clear_old_result(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = Mock()
    client.chat.completions.create.return_value = completion_response()
    monkeypatch.setattr(explain, "OpenAI", Mock(return_value=client))
    app = AppTest.from_file(str(APP)).run()
    click(app, "Рассчитать сценарий")
    app.selectbox(key="ai_model").select("gpt-4.1").run()
    click(app, "Получить AI-объяснение")
    assert any("AI-комментарий: gpt-4.1" in caption.value for caption in app.caption)
    assert "95 из 100" in app.session_state["explanation"]
    choice = app.selectbox(key="decision_4_label")
    choice.select(next(option for option in choice.options if option.startswith("M4 —"))).run()
    assert not app.exception
    assert "calculation" not in app.session_state
    assert "explanation" not in app.session_state


def test_over_budget_is_visible_and_no_score_is_calculated():
    app = AppTest.from_file(str(APP)).run()
    choices = {0: "M3", 1: "M5", 2: "M8", 3: "M12", 4: "M10"}
    for index, initiative in choices.items():
        widget = app.selectbox(key=f"decision_{index}_label")
        widget.select(next(label for label in widget.options if label.startswith(initiative + " —"))).run()
    click(app, "Рассчитать сценарий")
    assert any("Превышен бюджет" in error.value for error in app.error)
    assert "Astana Quality of Life Score" not in metrics(app)
