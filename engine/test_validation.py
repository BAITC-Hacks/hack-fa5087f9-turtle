import pytest

from scoring import load_data, validate_decisions


DISTRICTS = ["Есиль", "Алматы", "Сарыарка", "Байконур", "Нура"]


@pytest.fixture
def game_data():
    _, initiatives, rules = load_data()
    return initiatives, rules


def decisions(*items):
    return [{"id": initiative_id, "district": district} for initiative_id, district in items]


VALID = decisions(
    ("M7", "Нура"),
    ("M8", "Нура"),
    ("M10", "Нура"),
    ("M12", None),
    ("M5", "Сарыарка"),
)


def check(game_data, selection):
    initiatives, rules = game_data
    return validate_decisions(selection, initiatives, rules)


@pytest.mark.parametrize("count", [0, 4, 6])
def test_requires_exactly_five_decisions(game_data, count):
    sample = (VALID + [{"id": "M1", "district": "Есиль"}])[:count]
    assert check(game_data, sample)[0] is False


def test_accepts_valid_example(game_data):
    assert check(game_data, VALID) == (True, "")


def test_rejects_duplicate_even_in_different_districts(game_data):
    sample = decisions(("M7", "Нура"), ("M7", "Есиль"), *[(x["id"], x["district"]) for x in VALID[2:]])
    assert check(game_data, sample)[0] is False


def test_rejects_unknown_id(game_data):
    sample = [{**VALID[0], "id": "M99"}, *VALID[1:]]
    assert check(game_data, sample)[0] is False


@pytest.mark.parametrize("district", [None, "Вымышленный район"])
def test_district_measure_requires_known_district(game_data, district):
    sample = [{**VALID[0], "district": district}, *VALID[1:]]
    assert check(game_data, sample)[0] is False


@pytest.mark.parametrize("district", ["Есиль", "город"])
def test_city_measure_rejects_district(game_data, district):
    sample = [*VALID[:3], {"id": "M12", "district": district}, VALID[4]]
    assert check(game_data, sample)[0] is False


def test_city_measure_accepts_missing_district(game_data):
    sample = [*VALID[:3], {"id": "M12"}, VALID[4]]
    assert check(game_data, sample) == (True, "")


def test_rejects_three_from_one_direction(game_data):
    sample = decisions(
        ("M7", "Нура"), ("M8", "Нура"), ("M9", "Нура"),
        ("M10", "Алматы"), ("M12", None),
    )
    assert check(game_data, sample)[0] is False


def test_accepts_total_cost_exactly_budget(game_data):
    sample = decisions(
        ("M3", "Есиль"), ("M6", None), ("M9", "Нура"),
        ("M10", "Алматы"), ("M13", "Байконур"),
    )
    assert sum(next(i["cost"] for i in game_data[0] if i["id"] == d["id"]) for d in sample) == 100
    assert check(game_data, sample) == (True, "")


def test_rejects_over_budget(game_data):
    sample = decisions(
        ("M3", "Есиль"), ("M5", "Сарыарка"), ("M8", "Нура"),
        ("M10", "Алматы"), ("M12", None),
    )
    assert check(game_data, sample)[0] is False


@pytest.mark.parametrize("pair,same_district,valid", [
    (("M1", "M3"), True, False),
    (("M1", "M3"), False, False),
    (("M4", "M7"), True, False),
    (("M4", "M7"), False, True),
    (("M5", "M13"), True, False),
    (("M5", "M13"), False, True),
])
def test_incompatible_pairs(game_data, pair, same_district, valid):
    first, second = pair
    district_a = "Нура"
    district_b = "Нура" if same_district else "Есиль"
    extras = [("M10", "Алматы"), ("M12", None), ("M9", "Сарыарка")]
    sample = decisions((first, district_a), (second, district_b), *extras)
    assert check(game_data, sample)[0] is valid


def test_global_incompatibility_scope_is_declared_in_rules(game_data):
    _, rules = game_data
    assert ["M1", "M3"] in rules["global_incompatible_pairs"]


def test_validation_does_not_depend_on_order(game_data):
    assert check(game_data, VALID) == check(game_data, list(reversed(VALID)))
