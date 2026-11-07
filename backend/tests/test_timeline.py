"""Tests for backend.analysis.timeline"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from analysis.models import FoodLogEntry, SymptomLogEntry
from analysis.timeline import BinStatus, build_timeline

NY = ZoneInfo("America/New_York")
TOKYO = ZoneInfo("Asia/Tokyo")
UTC = timezone.utc
FAR_FUTURE = datetime(2027, 6, 1, tzinfo=UTC)


@dataclass(frozen=True)
class FakeMatch:
    ingredient_id: str
    components: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class FakeRoute:
    route: str
    family: str | None = None


TAXONOMY = {
    "milk": FakeMatch("milk", {"lactose": 3, "fodmap": 1}),
    "cheese": FakeMatch("cheese", {"lactose": 1, "histamine": 2}),
    "bread": FakeMatch("bread", {"gluten": 3, "fodmap": 2}),
}

ROUTES = {
    "bloating": FakeRoute("model", "gi"),
    "cramps": FakeRoute("model", "gi"),
    "itch": FakeRoute("model", "skin"),
    "throat_swelling": FakeRoute("allergy_like"),
    "chest_pain": FakeRoute("red_flag"),
    "mystery": FakeRoute("model", None),
}


def fake_lookup(name: str) -> FakeMatch:
    return TAXONOMY.get(name, FakeMatch("unknown"))


def fake_route(sensation: str, location: str) -> FakeRoute:
    return ROUTES[sensation]


def local(y, m, d, h, mi=0, tz=NY, fold=0) -> datetime:
    return datetime(y, m, d, h, mi, tzinfo=tz, fold=fold)


def run(
    foods=(),
    symptoms=(),
    checkins=(),
    tz=NY,
    start=date(2026, 1, 1),
    end=date(2026, 12, 31),
    now=FAR_FUTURE,
):
    return build_timeline(
        food_logs=list(foods),
        symptom_logs=list(symptoms),
        no_symptom_days=list(checkins),
        tz=tz,
        start_date=start,
        end_date=end,
        now=now,
        lookup=fake_lookup,
        route=fake_route,
    )


def only_bin(bins):
    assert len(bins) == 1, bins
    return bins[0]


def test_no_logs_returns_no_bins():
    assert run() == []


def test_late_evening_meal_stays_on_local_day():
    # 23:30 New York is 04:30 UTC the next day; it must stay on Jan 10 locally.
    meal = FoodLogEntry(timestamp=local(2026, 1, 10, 23, 30), ingredients=["milk"])
    b = only_bin(run(foods=[meal]))
    assert b.start == local(2026, 1, 10, 21)
    assert b.start.date() == date(2026, 1, 10)


def test_bin_boundary_is_start_inclusive():
    bins = run(
        foods=[
            FoodLogEntry(timestamp=local(2026, 1, 10, 2, 59), ingredients=["milk"]),
            FoodLogEntry(timestamp=local(2026, 1, 10, 3, 0), ingredients=["milk"]),
        ]
    )
    assert [b.start for b in bins] == [local(2026, 1, 10, 0), local(2026, 1, 10, 3)]


def test_meals_in_same_bin_share_one_bin():
    only_bin(
        run(
            foods=[
                FoodLogEntry(timestamp=local(2026, 1, 10, 18, 5), ingredients=["milk"]),
                FoodLogEntry(timestamp=local(2026, 1, 10, 20, 55), ingredients=["bread"]),
            ]
        )
    )


def test_bins_are_sorted_regardless_of_input_order():
    bins = run(
        foods=[
            FoodLogEntry(timestamp=local(2026, 1, 11, 9), ingredients=["milk"]),
            FoodLogEntry(timestamp=local(2026, 1, 10, 9), ingredients=["milk"]),
            FoodLogEntry(timestamp=local(2026, 1, 10, 6), ingredients=["milk"]),
        ]
    )
    starts = [b.start for b in bins]
    assert starts == sorted(starts)


def test_date_range_is_inclusive_and_uses_local_dates():
    bins = run(
        foods=[
            # first moment of start_date -> in
            FoodLogEntry(timestamp=local(2026, 1, 1, 0, 0), ingredients=["milk"]),
            # last minute of end_date -> in
            FoodLogEntry(timestamp=local(2026, 1, 3, 23, 59), ingredients=["milk"]),
            # Jan 1 in UTC but Dec 31 in New York -> out
            FoodLogEntry(timestamp=datetime(2026, 1, 1, 3, 0, tzinfo=UTC), ingredients=["milk"]),
            # day after end_date -> out
            FoodLogEntry(timestamp=local(2026, 1, 4, 0, 0), ingredients=["milk"]),
        ],
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
    )
    assert [b.start for b in bins] == [local(2026, 1, 1, 0), local(2026, 1, 3, 21)]


def test_same_instant_bins_differently_per_timezone():
    # 14:00 UTC is 09:00 in New York and 23:00 in Tokyo.
    meal = FoodLogEntry(timestamp=datetime(2026, 1, 10, 14, 0, tzinfo=UTC), ingredients=["milk"])
    assert only_bin(run(foods=[meal], tz=NY)).start == local(2026, 1, 10, 9)
    assert only_bin(run(foods=[meal], tz=TOKYO)).start == local(2026, 1, 10, 21, tz=TOKYO)


def test_component_levels_take_max_not_sum():
    b = only_bin(
        run(
            foods=[
                FoodLogEntry(timestamp=local(2026, 1, 10, 12), ingredients=["milk", "cheese"]),
                # second meal in the same bin
                FoodLogEntry(timestamp=local(2026, 1, 10, 13), ingredients=["milk"]),
            ]
        )
    )
    assert b.components == {"lactose": 3, "fodmap": 1, "histamine": 2}


def test_unknown_ingredients_are_kept_separately():
    meal = FoodLogEntry(timestamp=local(2026, 1, 10, 12), ingredients=["milk", "grandmas sauce"])
    b = only_bin(run(foods=[meal]))
    assert b.unmatched_ingredients == {"grandmas sauce"}
    assert b.components == {"lactose": 3, "fodmap": 1}


def test_fully_unknown_meal_still_produces_a_food_bin():
    meal = FoodLogEntry(timestamp=local(2026, 1, 10, 12), ingredients=["mystery stew"])
    b = only_bin(run(foods=[meal], now=local(2026, 1, 10, 14)))
    assert b.components == {}
    assert b.unmatched_ingredients == {"mystery stew"}
    assert b.status == BinStatus.PENDING  # still treated as a meal for the 36h rule


def test_symptoms_take_max_intensity_per_family():
    b = only_bin(
        run(
            symptoms=[
                SymptomLogEntry(
                    timestamp=local(2026, 1, 10, 12),
                    symptom_name="bloating",
                    sensation="bloating",
                    location="stomach",
                    intensity=4,
                ),
                SymptomLogEntry(
                    timestamp=local(2026, 1, 10, 13),
                    symptom_name="cramps",
                    sensation="cramps",
                    location="stomach",
                    intensity=7,
                ),
                SymptomLogEntry(
                    timestamp=local(2026, 1, 10, 14), symptom_name="itch", sensation="itch", location="arm", intensity=2
                ),
            ]
        )
    )
    assert b.symptoms == {"gi": 7, "skin": 2}


def test_only_model_routed_symptoms_make_bins():
    bins = run(
        symptoms=[
            SymptomLogEntry(
                timestamp=local(2026, 1, 10, 12),
                symptom_name="chest_pain",
                sensation="chest_pain",
                location="chest",
                intensity=5,
            ),
            SymptomLogEntry(
                timestamp=local(2026, 1, 10, 15),
                symptom_name="throat_swelling",
                sensation="throat_swelling",
                location="throat",
                intensity=5,
            ),
            # model route but no family
            SymptomLogEntry(
                timestamp=local(2026, 1, 10, 18),
                symptom_name="mystery",
                sensation="mystery",
                location="back",
                intensity=5,
            ),
        ]
    )
    assert bins == []


def test_symptom_only_bin_is_always_usable():
    # No check-ins at all and the bin is far in the past: still usable, no food.
    s = SymptomLogEntry(
        timestamp=local(2026, 1, 10, 12), symptom_name="bloating", sensation="bloating", location="stomach", intensity=5
    )
    b = only_bin(run(symptoms=[s]))
    assert b.status == BinStatus.USABLE
    assert b.components == {}


def test_food_and_symptom_in_same_bin():
    meal = FoodLogEntry(timestamp=local(2026, 1, 10, 12), ingredients=["milk"])
    s = SymptomLogEntry(
        timestamp=local(2026, 1, 10, 14), symptom_name="itch", sensation="itch", location="arm", intensity=3
    )
    b = only_bin(run(foods=[meal], symptoms=[s]))
    assert b.components
    assert b.symptoms == {"skin": 3}


MEAL = FoodLogEntry(timestamp=local(2026, 1, 10, 13), ingredients=["milk"])
JAN_10_AND_11 = [date(2026, 1, 10), date(2026, 1, 11)]


def status(**kwargs) -> BinStatus:
    return only_bin(run(foods=[kwargs.pop("meal", MEAL)], **kwargs)).status


def test_pending_while_window_open_and_past_days_checked_in():
    assert status(checkins=[date(2026, 1, 10)], now=local(2026, 1, 11, 10)) == BinStatus.PENDING


def test_today_does_not_need_a_checkin_yet():
    # Meal day is today; nothing checked in; window open -> pending, not unusable.
    assert status(now=local(2026, 1, 10, 20)) == BinStatus.PENDING


def test_unusable_wins_over_pending():
    # Window still open, but Jan 10 is in the past and wasn't checked in.
    assert status(now=local(2026, 1, 11, 10)) == BinStatus.UNUSABLE


def test_usable_once_window_over_and_all_days_checked_in():
    assert status(checkins=JAN_10_AND_11, now=local(2026, 1, 12, 8)) == BinStatus.USABLE


def test_missing_second_day_is_unusable():
    assert status(checkins=[date(2026, 1, 10)], now=local(2026, 1, 12, 8)) == BinStatus.UNUSABLE


def test_window_end_is_exclusive():
    # Window ends exactly at Jan 12 00:00, so Jan 12 is never required.
    assert status(checkins=JAN_10_AND_11, now=local(2026, 1, 14, 8)) == BinStatus.USABLE


def test_now_exactly_at_window_end_is_usable():
    window_end = local(2026, 1, 12, 0)
    assert status(checkins=JAN_10_AND_11, now=window_end) == BinStatus.USABLE
    almost = window_end - timedelta(microseconds=1)
    assert status(checkins=JAN_10_AND_11, now=almost) == BinStatus.PENDING


def test_late_meal_window_touches_three_days():
    # 22:00 -> bin starts 21:00, window ends Jan 12 09:00, so Jan 12 counts.
    late = FoodLogEntry(timestamp=local(2026, 1, 10, 22), ingredients=["milk"])
    now = local(2026, 1, 13, 8)
    assert status(meal=late, checkins=JAN_10_AND_11, now=now) == BinStatus.UNUSABLE
    all_three = [*JAN_10_AND_11, date(2026, 1, 12)]
    assert status(meal=late, checkins=all_three, now=now) == BinStatus.USABLE


def test_any_symptom_log_checks_in_the_day_even_non_model_routes():
    # Red-flag and allergy-like logs make no bins, but the user did open the app and log.
    logs = [
        SymptomLogEntry(
            timestamp=local(2026, 1, 10, 20),
            symptom_name="chest_pain",
            sensation="chest_pain",
            location="chest",
            intensity=5,
        ),
        SymptomLogEntry(
            timestamp=local(2026, 1, 11, 20),
            symptom_name="throat_swelling",
            sensation="throat_swelling",
            location="throat",
            intensity=5,
        ),
    ]
    assert status(symptoms=logs, now=local(2026, 1, 12, 8)) == BinStatus.USABLE


def test_symptom_checkin_uses_local_date():
    # 03:00 UTC Jan 12 is 22:00 Jan 11 in New York -> checks in Jan 11.
    log = SymptomLogEntry(
        timestamp=datetime(2026, 1, 12, 3, 0, tzinfo=UTC),
        symptom_name="chest_pain",
        sensation="chest_pain",
        location="chest",
        intensity=5,
    )
    result = status(symptoms=[log], checkins=[date(2026, 1, 10)], now=local(2026, 1, 12, 8))
    assert result == BinStatus.USABLE


def test_symptoms_outside_range_still_count_as_checkins():
    log = SymptomLogEntry(
        timestamp=local(2026, 1, 11, 20),
        symptom_name="chest_pain",
        sensation="chest_pain",
        location="chest",
        intensity=5,
    )
    result = status(
        symptoms=[log],
        checkins=[date(2026, 1, 10)],
        start=date(2026, 1, 10),
        end=date(2026, 1, 10),
        now=local(2026, 1, 12, 8),
    )
    assert result == BinStatus.USABLE


def test_fall_back_repeated_hour_lands_in_one_bin():
    first = local(2026, 11, 1, 1, 30, fold=0)  # 01:30 EDT = 05:30 UTC
    second = local(2026, 11, 1, 1, 30, fold=1)  # 01:30 EST = 06:30 UTC
    assert first.astimezone(UTC) != second.astimezone(UTC)
    bins = run(
        foods=[
            FoodLogEntry(timestamp=first, ingredients=["milk"]),
            FoodLogEntry(timestamp=second, ingredients=["milk"]),
            FoodLogEntry(timestamp=local(2026, 11, 1, 3, 30), ingredients=["milk"]),
        ]
    )
    assert len(bins) == 2
    assert bins[0].start.astimezone(UTC) == datetime(2026, 11, 1, 4, tzinfo=UTC)  # 00:00 EDT
    assert bins[1].start.astimezone(UTC) == datetime(2026, 11, 1, 8, tzinfo=UTC)  # 03:00 EST
    # The first bin of the day covers 4 real hours (documented choice: wall-clock bins).


def test_spring_forward_skipped_hour():
    bins = run(
        foods=[
            FoodLogEntry(timestamp=local(2026, 3, 8, 1, 30), ingredients=["milk"]),
            FoodLogEntry(timestamp=local(2026, 3, 8, 3, 30), ingredients=["milk"]),
        ]
    )
    assert len(bins) == 2
    assert bins[0].start.astimezone(UTC) == datetime(2026, 3, 8, 5, tzinfo=UTC)  # 00:00 EST
    assert bins[1].start.astimezone(UTC) == datetime(2026, 3, 8, 7, tzinfo=UTC)  # 03:00 EDT
    # The first bin of the day covers only 2 real hours.


def _assert_day_tiles_cleanly(day: date):
    day_start = datetime.combine(day, datetime.min.time(), tzinfo=NY).astimezone(UTC)
    day_end = datetime.combine(day + timedelta(days=1), datetime.min.time(), tzinfo=NY).astimezone(UTC)
    instants = []
    t = day_start
    while t < day_end:
        instants.append(t)
        t += timedelta(minutes=30)

    bins = run(foods=[FoodLogEntry(timestamp=t, ingredients=["milk"]) for t in instants])
    starts = [b.start.astimezone(UTC) for b in bins]
    assert len(bins) == 8
    assert all(b.start.date() == day for b in bins)
    assert starts == sorted(set(starts))  # strictly increasing -> no overlaps
    assert starts[0] == day_start
    edges = [*starts, day_end]
    for t in instants:  # every real instant falls in exactly one [start, next_start)
        assert sum(edges[i] <= t < edges[i + 1] for i in range(8)) == 1


def test_fall_back_day_has_no_gaps_or_overlaps():
    _assert_day_tiles_cleanly(date(2026, 11, 1))  # 25-hour day


def test_spring_forward_day_has_no_gaps_or_overlaps():
    _assert_day_tiles_cleanly(date(2026, 3, 8))  # 23-hour day


def test_window_is_36_real_hours_across_spring_forward():
    # Bin Mar 7 12:00 EST (17:00 UTC) + 36h = Mar 9 05:00 UTC = 01:00 EDT -> touches Mar 9.
    meal = FoodLogEntry(timestamp=local(2026, 3, 7, 13), ingredients=["milk"])
    two_days = [date(2026, 3, 7), date(2026, 3, 8)]
    now = local(2026, 3, 10, 12)
    assert status(meal=meal, checkins=two_days, now=now) == BinStatus.UNUSABLE
    assert status(meal=meal, checkins=[*two_days, date(2026, 3, 9)], now=now) == BinStatus.USABLE


def test_window_is_36_real_hours_across_fall_back():
    # Bin Oct 31 12:00 EDT (16:00 UTC) + 36h = Nov 2 04:00 UTC = Nov 1 23:00 EST -> Nov 2 not touched.
    meal = FoodLogEntry(timestamp=local(2026, 10, 31, 13), ingredients=["milk"])
    two_days = [date(2026, 10, 31), date(2026, 11, 1)]
    assert status(meal=meal, checkins=two_days, now=local(2026, 11, 3, 12)) == BinStatus.USABLE
