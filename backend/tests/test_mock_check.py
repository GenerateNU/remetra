"""Signal check: measured from the data alone, trigger users stand out and no-trigger users don't."""

from datetime import date, datetime, timedelta, timezone

import pytest

from scripts.mock_users.check import assess_users, chance_by_background, main, measure
from scripts.mock_users.generate import generate_users, write_truth_file
from scripts.mock_users.shapes import MealLog, MockFood, MockUserData, SymptomEvent, SymptomKind, load_user_types

END = date(2026, 11, 1)
TYPES, RATE = load_user_types()
TRIGGERS = [t.trigger for t in TYPES.values() if t.trigger]
LACTOSE = TYPES["lactose"]
NO_TRIGGER = TYPES["no_trigger"]
MILKY = MockFood("Mac and cheese", ["pasta", "cheese", "milk", "butter"])
PLAIN = MockFood("Quinoa salad", ["quinoa", "cucumber", "olive oil"])


def _meals(food, count):
    return [
        MealLog(food.name, datetime(2026, 10, 1, 12, tzinfo=timezone.utc) + timedelta(days=i)) for i in range(count)
    ]


def _cramps_after(meals, planted=True):
    return [SymptomEvent(LACTOSE.trigger.symptom, 6, m.timestamp + timedelta(hours=2), 30, planted) for m in meals]


def _fatigue(count):
    start = datetime(2026, 10, 1, 8, tzinfo=timezone.utc)
    return [
        SymptomEvent(SymptomKind("Fatigue", "Whole Body"), 2, start + timedelta(days=i), 20, False)
        for i in range(count)
    ]


def _user(user_type, meals, symptoms, foods=(MILKY, PLAIN)):
    return MockUserData("mock_001", user_type, list(foods), meals, symptoms)


def _report(user):
    return assess_users([user], TRIGGERS, RATE)[0]


def test_trigger_user_stands_out():
    meals = _meals(MILKY, 10)
    report = _report(_user(LACTOSE, meals + _meals(PLAIN, 10), _cramps_after(meals)))

    assert report.problem is None
    assert report.signal.trigger_meals == 10
    assert report.signal.follow_rate == 1.0


def test_follow_is_measured_from_symptoms_not_the_planted_label():
    meals = _meals(MILKY, 10)
    report = _report(_user(LACTOSE, meals, _cramps_after(meals, planted=False)))

    assert report.signal.follow_rate == 1.0


def test_trigger_user_whose_reactions_do_not_follow_fails():
    meals = _meals(MILKY, 10)
    report = _report(_user(LACTOSE, meals, _cramps_after(meals[:2])))

    assert report.problem == "trigger does not stand out"


def test_few_trigger_meals_are_not_judged():
    meals = _meals(MILKY, 2)
    report = _report(_user(LACTOSE, meals, []))

    assert not report.signal.judged
    assert report.problem is None


def test_trigger_never_eaten_is_not_judged():
    report = _report(_user(LACTOSE, _meals(PLAIN, 8), [], foods=[PLAIN]))

    assert report.signal.trigger_meals == 0
    assert report.signal.follow_rate is None
    assert report.problem is None


def test_no_trigger_user_with_background_only_does_not_stand_out():
    report = _report(_user(NO_TRIGGER, _meals(MILKY, 10), _fatigue(9)))

    assert report.problem is None


def test_no_trigger_user_whose_symptoms_follow_a_trigger_fails():
    meals = _meals(MILKY, 10)
    report = _report(_user(NO_TRIGGER, meals, _cramps_after(meals, planted=False)))

    assert report.problem == "lactose stands out for a no-trigger user"


def test_chance_by_background_is_small_and_grows_with_rate():
    trigger = LACTOSE.trigger

    assert 0 < chance_by_background(trigger, RATE) < 0.05
    assert chance_by_background(trigger, RATE * 2) > chance_by_background(trigger, RATE)
    assert measure(_user(LACTOSE, [], []), trigger, RATE).by_chance == chance_by_background(trigger, RATE)


def test_zero_users():
    assert assess_users([], TRIGGERS, RATE) == []


@pytest.mark.parametrize("seed", [1, 7, 42])
def test_generated_users_pass(seed):
    reports = assess_users(generate_users(seed, 20, END), TRIGGERS, RATE)

    assert [r for r in reports if r.problem] == []


def test_main_checks_the_users_in_the_truth_file(tmp_path, capsys):
    path = tmp_path / "truth.json"
    write_truth_file(generate_users(42, 8, END), path, seed=42, end_date=END, days=60)

    assert main(["--truth", str(path)]) == 0
    out = capsys.readouterr().out
    assert "mock_008" in out
    assert "Signal check passed for 8 users" in out


def test_main_zero_users_passes(tmp_path, capsys):
    path = tmp_path / "truth.json"
    write_truth_file([], path, seed=1, end_date=END, days=60)

    assert main(["--truth", str(path)]) == 0
    assert "Signal check passed for 0 users" in capsys.readouterr().out


def test_main_fails_when_a_user_does_not_stand_out(tmp_path, capsys, monkeypatch):
    path = tmp_path / "truth.json"
    write_truth_file(generate_users(1, 1, END), path, seed=1, end_date=END, days=60)
    meals = _meals(MILKY, 10)
    monkeypatch.setattr("scripts.mock_users.check.generate_users", lambda *a, **k: [_user(LACTOSE, meals, [])])

    assert main(["--truth", str(path)]) == 1
    assert "mock_001: trigger does not stand out" in capsys.readouterr().out


def test_main_without_truth_file(tmp_path, capsys):
    assert main(["--truth", str(tmp_path / "missing.json")]) == 1
    assert "Run `just mock` first" in capsys.readouterr().out
