from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).with_name("app.py")


def open_ui(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return AppTest.from_file(str(APP)).run()


def option_for(widget, initiative_id):
    return next(label for label in widget.options if label.startswith(f"{initiative_id} —"))


def test_starting_cards_and_full_table_come_from_district_dataset(monkeypatch):
    app = open_ui(monkeypatch)

    assert not app.exception
    assert [
        app.selectbox(key=f"decision_{slot}_label").value.split(" — ", 1)[0]
        for slot in range(5)
    ] == ["M7", "M8", "M10", "M12", "M5"]
    assert len(app.table[0].value) == 5
    nura = app.table[0].value.set_index("Район").loc["Нура"]
    assert nura["Доля населения"] == "16%"
    assert nura["S1 · Школы и детсады"] == 38
    assert nura["S2 · Поликлиники и первичная медпомощь"] == 35
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Стоимость решений"] == "95 у.е."
    assert metrics["Остаток бюджета"] == "5 у.е."
    assert metrics["Выбрано позиций"] == "5 из 5"


def test_switching_city_and_district_initiatives_adds_and_clears_region(monkeypatch):
    app = open_ui(monkeypatch)
    city_slot = app.selectbox(key="decision_0_label")
    city_slot.select(option_for(city_slot, "M2")).run()

    assert not app.exception
    assert "decision_0_district" not in app.session_state
    assert "decision_0_district" not in {widget.key for widget in app.selectbox}
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Стоимость решений"] == "93 у.е."
    assert metrics["Остаток бюджета"] == "7 у.е."

    fourth_slot = app.selectbox(key="decision_3_label")
    fourth_slot.select(option_for(fourth_slot, "M4")).run()
    assert "decision_3_district" in {widget.key for widget in app.selectbox}
    assert app.selectbox(key="decision_3_district").value == "Есиль"

    fourth_slot = app.selectbox(key="decision_3_label")
    fourth_slot.select(option_for(fourth_slot, "M12")).run()
    assert "decision_3_district" not in {widget.key for widget in app.selectbox}
    assert "decision_3_district" not in app.session_state


def test_duplicate_selection_prevents_score_calculation(monkeypatch):
    app = open_ui(monkeypatch)
    third_slot = app.selectbox(key="decision_2_label")
    third_slot.select(option_for(third_slot, "M7")).run()

    assert not app.exception
    assert any("выбрано больше одного раза" in item.value for item in app.error)
    calculate = next(button for button in app.button if button.label == "Рассчитать сценарий")
    calculate.click().run()
    assert any("выбрано больше одного раза" in item.value for item in app.error)
    assert "Astana Quality of Life Score" not in {
        metric.label for metric in app.metric
    }
