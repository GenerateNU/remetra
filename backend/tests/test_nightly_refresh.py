"""Unit tests for analysis.nightly_refresh.symptom_meal_map.

Behavior under test:
- Only symptoms with timestamp in [now - 24h, now] (inclusive) are considered.
- Each considered symptom links to every meal with timestamp in
  [symptom - lookback, symptom] (inclusive), where lookback is 48h for the
  "SKIN" family and 36h otherwise.
- One SymptomMealMap is returned per input meal, in input order, mapping
  symptom id -> (symptom.timestamp - meal.timestamp).

Most tests pass a fixed `now` so boundaries can be tested exactly.
TestNowArgument covers the `now` parameter contract.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from analysis.nightly_refresh import SymptomMealMap, symptom_meal_map
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse

NOW = datetime(2026, 3, 16, 12, 0, 0, tzinfo=timezone.utc)
TICK = timedelta(microseconds=1)
USERNAME = "test_user"


class FamilySymptomLog(SymptomLogResponse):
    """SymptomLogResponse doesn't define `family` yet; symptom_meal_map reads it."""

    family: str


def make_meal(timestamp: datetime) -> FoodLogResponse:
    return FoodLogResponse(
        id=uuid4(),
        food_id=uuid4(),
        username=USERNAME,
        timestamp=timestamp,
        created_at=timestamp + timedelta(minutes=7),  # logged after eating; must not be used as food_time
    )


def make_symptom(timestamp: datetime, family: str = "DIGESTIVE") -> FamilySymptomLog:
    return FamilySymptomLog(
        id=uuid4(),
        symptom_id=uuid4(),
        username=USERNAME,
        intensity=5,
        timestamp=timestamp,
        created_at=timestamp + timedelta(minutes=3),  # logged after onset; must not be used for deltas
        family=family,
    )


def hours(h: float) -> timedelta:
    return timedelta(hours=h)


def run(meals, symptoms, now: datetime = NOW) -> list[SymptomMealMap]:
    return symptom_meal_map(meals, symptoms, now=now)


def linked(meal: FoodLogResponse, symptom: FamilySymptomLog, now: datetime = NOW) -> dict[UUID, timedelta]:
    """Run the map for a single meal/symptom pair and return that meal's symptom dict."""
    [result] = run([meal], [symptom], now=now)
    return result.symptoms


class TestOutputShape:
    def test_empty_inputs_return_empty_list(self):
        assert run([], []) == []

    def test_no_meals_returns_empty_list_even_with_symptoms(self):
        symptoms = [make_symptom(NOW - hours(1)), make_symptom(NOW - hours(2), family="SKIN")]

        assert run([], symptoms) == []

    def test_no_symptoms_returns_one_empty_map_per_meal(self):
        meals = [make_meal(NOW - hours(h)) for h in (1, 5, 30)]

        result = run(meals, [])

        assert len(result) == 3
        assert all(m.symptoms == {} for m in result)

    def test_one_map_per_meal_in_input_order_including_unlinked_meals(self):
        unlinked_old = make_meal(NOW - hours(100))
        linked_meal = make_meal(NOW - hours(3))
        unlinked_after = make_meal(NOW - hours(0.5))
        symptom = make_symptom(NOW - hours(1))
        meals = [unlinked_old, linked_meal, unlinked_after]

        result = run(meals, [symptom])

        assert [m.food_log for m in result] == meals
        assert [m.symptoms for m in result] == [{}, {symptom.id: hours(2)}, {}]

    def test_map_fields_reference_the_input_meal(self):
        meal = make_meal(NOW - hours(4))

        [result] = run([meal], [])

        assert isinstance(result, SymptomMealMap)
        assert result.food_log is meal
        assert result.food_time == meal.timestamp

    def test_symptoms_keyed_by_symptom_log_id_not_symptom_id(self):
        meal = make_meal(NOW - hours(2))
        symptom = make_symptom(NOW - hours(1))

        result = linked(meal, symptom)

        assert list(result) == [symptom.id]
        assert symptom.symptom_id not in result

    def test_inputs_are_not_mutated(self):
        meals = [make_meal(NOW - hours(2)), make_meal(NOW - hours(50))]
        symptoms = [make_symptom(NOW - hours(1)), make_symptom(NOW - hours(30))]
        meals_before = [m.model_copy() for m in meals]
        symptoms_before = [s.model_copy() for s in symptoms]

        run(meals, symptoms)

        assert meals == meals_before
        assert symptoms == symptoms_before


class TestSymptomRecencyWindow:
    """Symptoms are only considered if timestamp is within [now - 24h, now]."""

    @pytest.mark.parametrize(
        "symptom_offset",
        [
            pytest.param(timedelta(0), id="exactly-now"),
            pytest.param(hours(12), id="mid-window"),
            pytest.param(hours(24) - TICK, id="just-inside-24h"),
            pytest.param(hours(24), id="exactly-24h-ago"),
        ],
    )
    def test_symptom_inside_window_is_considered(self, symptom_offset):
        symptom = make_symptom(NOW - symptom_offset)
        meal = make_meal(symptom.timestamp - hours(1))

        assert linked(meal, symptom) == {symptom.id: hours(1)}

    @pytest.mark.parametrize(
        "symptom_time",
        [
            pytest.param(NOW - hours(24) - TICK, id="just-older-than-24h"),
            pytest.param(NOW - hours(30), id="well-older-than-24h"),
            pytest.param(NOW + TICK, id="just-in-future"),
            pytest.param(NOW + hours(5), id="well-in-future"),
        ],
    )
    def test_symptom_outside_window_is_ignored(self, symptom_time):
        symptom = make_symptom(symptom_time)
        meal = make_meal(symptom_time - hours(1))  # would otherwise be linked

        assert linked(meal, symptom) == {}

    def test_skin_symptom_uses_same_24h_recency_window(self):
        symptom = make_symptom(NOW - hours(24) - TICK, family="SKIN")
        meal = make_meal(symptom.timestamp - hours(1))

        assert linked(meal, symptom) == {}

    def test_window_is_relative_to_now_argument(self):
        symptom = make_symptom(NOW - hours(20))
        meal = make_meal(symptom.timestamp - hours(1))

        assert linked(meal, symptom, now=NOW) == {symptom.id: hours(1)}
        assert linked(meal, symptom, now=NOW + hours(5)) == {}  # now 25h old
        assert linked(meal, symptom, now=NOW - hours(21)) == {}  # now in the future

    def test_now_in_non_utc_offset_gives_same_boundaries(self):
        now_plus_five = NOW.astimezone(timezone(timedelta(hours=5)))
        at_edge = make_symptom(NOW - hours(24))
        past_edge = make_symptom(NOW - hours(24) - TICK)
        meal = make_meal(NOW - hours(30))

        [result] = run([meal], [at_edge, past_edge], now=now_plus_five)

        assert result.symptoms == {at_edge.id: hours(6)}


class TestLookbackWindow:
    """Meals link to a symptom if timestamp is within [symptom - lookback, symptom]."""

    @pytest.mark.parametrize(
        "family, lookback",
        [
            pytest.param("DIGESTIVE", hours(36), id="default-36h"),
            pytest.param("SKIN", hours(48), id="skin-48h"),
        ],
    )
    @pytest.mark.parametrize(
        "meal_offset, expected_linked",
        [
            pytest.param(lambda lb: timedelta(0), True, id="same-instant-as-symptom"),
            pytest.param(lambda lb: TICK, True, id="just-before-symptom"),
            pytest.param(lambda lb: lb / 2, True, id="mid-lookback"),
            pytest.param(lambda lb: lb - TICK, True, id="just-inside-lookback"),
            pytest.param(lambda lb: lb, True, id="exactly-at-lookback-start"),
            pytest.param(lambda lb: lb + TICK, False, id="just-before-lookback-start"),
            pytest.param(lambda lb: -TICK, False, id="just-after-symptom"),
            pytest.param(lambda lb: -hours(1), False, id="well-after-symptom"),
        ],
    )
    def test_lookback_boundaries(self, family, lookback, meal_offset, expected_linked):
        symptom = make_symptom(NOW - hours(1), family=family)
        offset = meal_offset(lookback)
        meal = make_meal(symptom.timestamp - offset)

        expected = {symptom.id: offset} if expected_linked else {}
        assert linked(meal, symptom) == expected

    def test_meal_between_36h_and_48h_links_only_skin_symptom(self):
        symptom_time = NOW - hours(1)
        skin = make_symptom(symptom_time, family="SKIN")
        other = make_symptom(symptom_time, family="DIGESTIVE")
        meal = make_meal(symptom_time - hours(40))

        [result] = run([meal], [skin, other])

        assert result.symptoms == {skin.id: hours(40)}

    @pytest.mark.parametrize("family", ["skin", "Skin", " SKIN", "SKIN ", "SKINCARE", ""])
    def test_skin_family_match_is_exact_and_case_sensitive(self, family):
        symptom = make_symptom(NOW - hours(1), family=family)
        meal = make_meal(symptom.timestamp - hours(40))  # only inside a 48h lookback

        assert linked(meal, symptom) == {}

    def test_meal_older_than_24h_can_link_to_recent_symptom(self):
        """Meals are not filtered by recency, only by each symptom's lookback."""
        symptom = make_symptom(NOW - hours(23))
        meal = make_meal(NOW - hours(23) - hours(35))

        assert linked(meal, symptom) == {symptom.id: hours(35)}


class TestManyToMany:
    def test_meal_links_to_multiple_symptoms_with_individual_deltas(self):
        meal = make_meal(NOW - hours(10))
        s1 = make_symptom(NOW - hours(8))
        s2 = make_symptom(NOW - hours(2), family="SKIN")
        s3 = make_symptom(NOW)

        [result] = run([meal], [s1, s2, s3])

        assert result.symptoms == {s1.id: hours(2), s2.id: hours(8), s3.id: hours(10)}

    def test_symptom_links_to_multiple_meals(self):
        symptom = make_symptom(NOW - hours(1))
        meals = [make_meal(symptom.timestamp - hours(h)) for h in (0, 5, 20, 36)]

        result = run(meals, [symptom])

        assert [m.symptoms for m in result] == [
            {symptom.id: hours(0)},
            {symptom.id: hours(5)},
            {symptom.id: hours(20)},
            {symptom.id: hours(36)},
        ]

    def test_mixed_scenario_links_only_eligible_pairs(self):
        meal_60h = make_meal(NOW - hours(60))
        meal_40h = make_meal(NOW - hours(40))
        meal_30h = make_meal(NOW - hours(30))
        meal_10h = make_meal(NOW - hours(10))
        meal_2h = make_meal(NOW - hours(2))
        meal_now = make_meal(NOW)

        stale = make_symptom(NOW - hours(25))  # outside recency window
        digestive = make_symptom(NOW - hours(5))  # window [41h, 5h] ago
        skin = make_symptom(NOW - hours(4), family="SKIN")  # window [52h, 4h] ago
        latest = make_symptom(NOW - hours(1))  # window [37h, 1h] ago
        meals = [meal_60h, meal_40h, meal_30h, meal_10h, meal_2h, meal_now]

        result = run(meals, [stale, digestive, skin, latest])

        by_meal = {m.food_log.id: m.symptoms for m in result}
        assert by_meal[meal_60h.id] == {}
        assert by_meal[meal_40h.id] == {digestive.id: hours(35), skin.id: hours(36)}
        assert by_meal[meal_30h.id] == {
            digestive.id: hours(25),
            skin.id: hours(26),
            latest.id: hours(29),
        }
        assert by_meal[meal_10h.id] == {
            digestive.id: hours(5),
            skin.id: hours(6),
            latest.id: hours(9),
        }
        assert by_meal[meal_2h.id] == {latest.id: hours(1)}
        assert by_meal[meal_now.id] == {}

    def test_symptom_order_does_not_affect_result(self):
        meal = make_meal(NOW - hours(10))
        symptoms = [make_symptom(NOW - hours(h)) for h in (1, 3, 9)]

        forward = run([meal], symptoms)
        backward = run([meal], list(reversed(symptoms)))

        assert forward[0].symptoms == backward[0].symptoms

    def test_unsorted_meals_keep_input_order(self):
        symptom = make_symptom(NOW - hours(1))
        meals = [make_meal(NOW - hours(h)) for h in (5, 2, 30, 0.5, 10)]

        result = run(meals, [symptom])

        assert [m.food_log for m in result] == meals
        assert [m.symptoms for m in result] == [
            {symptom.id: hours(4)},
            {symptom.id: hours(1)},
            {symptom.id: hours(29)},
            {},
            {symptom.id: hours(9)},
        ]


class TestTimezones:
    def test_non_utc_offsets_compare_by_absolute_instant(self):
        plus_five = timezone(timedelta(hours=5))
        minus_eight = timezone(timedelta(hours=-8))
        symptom = make_symptom((NOW - hours(1)).astimezone(plus_five))
        meal = make_meal((NOW - hours(3)).astimezone(minus_eight))

        assert linked(meal, symptom) == {symptom.id: hours(2)}

    def test_recency_window_uses_absolute_instant_for_non_utc_symptom(self):
        plus_ten = timezone(timedelta(hours=10))
        symptom = make_symptom((NOW - hours(23)).astimezone(plus_ten))
        meal = make_meal(NOW - hours(24))

        assert linked(meal, symptom) == {symptom.id: hours(1)}

    def test_future_symptom_in_non_utc_offset_is_ignored(self):
        minus_eight = timezone(timedelta(hours=-8))
        # Wall clock looks 7h in the past, but the instant is 1h in the future.
        symptom = make_symptom((NOW + hours(1)).astimezone(minus_eight))
        meal = make_meal(NOW - hours(1))

        assert linked(meal, symptom) == {}


class TestNowArgument:
    """`now` is required so callers (e.g. the nightly job) pin one run time explicitly."""

    def test_omitting_now_raises_type_error(self):
        with pytest.raises(TypeError, match="now"):
            symptom_meal_map([], [])

    def test_now_accepted_positionally(self):
        symptom = make_symptom(NOW - hours(1))
        meal = make_meal(NOW - hours(2))

        [result] = symptom_meal_map([meal], [symptom], NOW)

        assert result.symptoms == {symptom.id: hours(1)}

    def test_same_now_gives_identical_results_across_calls(self):
        meals = [make_meal(NOW - hours(h)) for h in (2, 10, 30)]
        symptoms = [make_symptom(NOW - hours(h)) for h in (1, 5)]

        assert run(meals, symptoms) == run(meals, symptoms)


class TestSymptomMealMapDataclass:
    def test_equality_is_field_based(self):
        meal = make_meal(NOW)
        sid = uuid4()

        a = SymptomMealMap(food_log=meal, symptoms={sid: hours(1)}, food_time=meal.timestamp)
        b = SymptomMealMap(food_log=meal, symptoms={sid: hours(1)}, food_time=meal.timestamp)
        c = SymptomMealMap(food_log=meal, symptoms={}, food_time=meal.timestamp)

        assert a == b
        assert a != c

    def test_each_result_gets_its_own_symptoms_dict(self):
        meals = [make_meal(NOW - hours(1)), make_meal(NOW - hours(2))]

        result = run(meals, [])
        result[0].symptoms[uuid4()] = hours(1)

        assert result[1].symptoms == {}
