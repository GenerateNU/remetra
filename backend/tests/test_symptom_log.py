"""
Tests for symptom logs.

- Pydantic validation of SymptomLogCreate (intensity range, duration non-negative)
- washout_window, a pure function, and SymptomLogService.get_washout_status
- family, route and safety_message computed on POST /symptom-logs/ and GET /symptom-logs/user/me
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect

from models.symptom import Symptom
from models.symptom_log import SymptomLog
from schemas.symptom_log import SymptomFamily, SymptomLogCreate, SymptomRoute, SymptomRouteType
from services.symptom_log_service import SymptomLogService, washout_window
from services.symptom_routing import get_routing


def test_create_symptom_log_intensity_too_low():
    """Pydantic should reject intensity < 1."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            symptom_id=uuid4(),
            intensity=0,
            timestamp=datetime(2025, 1, 15, 10, 30),
        )


def test_create_symptom_log_intensity_too_high():
    """Pydantic should reject intensity > 10."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            symptom_id=uuid4(),
            intensity=11,
            timestamp=datetime(2025, 1, 15, 10, 30),
        )


def test_create_symptom_log_negative_duration():
    """Pydantic should reject duration < 0."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            symptom_id=uuid4(),
            intensity=5,
            timestamp=datetime(2025, 1, 15, 10, 30),
            duration=-10,
        )


NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
GI = SymptomRoute(route=SymptomRouteType.MODEL, family=SymptomFamily.GI)
SKIN = SymptomRoute(route=SymptomRouteType.MODEL, family=SymptomFamily.SKIN)
HEAD = SymptomRoute(route=SymptomRouteType.MODEL, family=SymptomFamily.HEAD)
OTHER = SymptomRoute(route=SymptomRouteType.MODEL, family=SymptomFamily.OTHER)
RED_FLAG = SymptomRoute(route=SymptomRouteType.RED_FLAG, safety_message="see a doctor")
ALLERGY_LIKE = SymptomRoute(route=SymptomRouteType.ALLERGY_LIKE, safety_message="get emergency care")


def hours_ago(h: float) -> datetime:
    return NOW - timedelta(hours=h)


# Cases from the ticket's testing notes
@pytest.mark.parametrize(
    ("symptoms", "active", "ends_at"),
    [
        pytest.param([(GI, 7, hours_ago(10))], True, hours_ago(10) + timedelta(hours=48), id="gi_7_ten_hours_ago"),
        pytest.param(
            [(GI, 3, hours_ago(10)), (SKIN, 2, hours_ago(4))],
            True,
            hours_ago(4) + timedelta(hours=48),
            id="gi_3_skin_2_same_day",
        ),
        pytest.param([(GI, 3, hours_ago(10)), (GI, 5, hours_ago(4))], False, None, id="gi_3_gi_5"),
        pytest.param([(ALLERGY_LIKE, 9, hours_ago(1))], False, None, id="allergy_like_9_is_not_model_data"),
        pytest.param([(GI, 8, hours_ago(72))], False, None, id="gi_8_three_days_ago"),
    ],
)
def test_washout_testing_notes(symptoms, active, ends_at):
    # Act
    status = washout_window(symptoms, NOW)
    # Assert
    assert (status.active, status.ends_at) == (active, ends_at)


def test_no_symptoms_is_inactive():
    # Act
    status = washout_window([], NOW)
    # Assert
    assert status.active is False
    assert status.ends_at is None


@pytest.mark.parametrize(("intensity", "active"), [(6, False), (7, True), (10, True)])
def test_high_intensity_model_symptom_triggers(intensity, active):
    # Act
    status = washout_window([(GI, intensity, hours_ago(1))], NOW)
    # Assert
    assert status.active is active


def test_washout_lasts_48h_from_trigger():
    # Act
    status = washout_window([(HEAD, 8, hours_ago(10))], NOW)
    # Assert
    assert status.ends_at == hours_ago(10) + timedelta(hours=48)


def test_washout_expires_after_48h():
    # Act
    status = washout_window([(HEAD, 8, hours_ago(48))], NOW)
    # Assert
    assert status.active is False
    assert status.ends_at is None


def test_other_family_counts_for_intensity():
    # Act
    status = washout_window([(OTHER, 7, hours_ago(1))], NOW)
    # Assert
    assert status.active is True


def test_safety_routes_never_trigger():
    # Act
    status = washout_window([(RED_FLAG, 10, hours_ago(1))], NOW)
    # Assert
    assert status.active is False


def test_two_families_within_24h_trigger_from_later_symptom():
    # Arrange
    symptoms = [(SKIN, 3, hours_ago(5)), (GI, 3, hours_ago(20))]
    # Act
    status = washout_window(symptoms, NOW)
    # Assert
    assert status.active is True
    assert status.ends_at == hours_ago(5) + timedelta(hours=48)


def test_two_families_more_than_24h_apart_do_not_trigger():
    # Act
    status = washout_window([(GI, 3, hours_ago(30)), (SKIN, 3, hours_ago(5))], NOW)
    # Assert
    assert status.active is False


def test_other_family_does_not_count_toward_span():
    # Act
    status = washout_window([(GI, 3, hours_ago(10)), (OTHER, 3, hours_ago(5))], NOW)
    # Assert
    assert status.active is False


def test_same_family_twice_does_not_trigger():
    # Act
    status = washout_window([(GI, 3, hours_ago(10)), (GI, 3, hours_ago(5))], NOW)
    # Assert
    assert status.active is False


def test_latest_trigger_extends_washout():
    # Arrange
    symptoms = [(GI, 9, hours_ago(40)), (HEAD, 8, hours_ago(2))]
    # Act
    status = washout_window(symptoms, NOW)
    # Assert
    assert status.ends_at == hours_ago(2) + timedelta(hours=48)


def test_symptoms_after_now_are_ignored():
    # Act
    status = washout_window([(GI, 9, NOW + timedelta(hours=1))], NOW)
    # Assert
    assert status.active is False


def test_get_washout_status_routes_signed_in_users_logs(db_session, authenticated_user):
    # Arrange
    headache = Symptom(username=authenticated_user["username"], name="headache", location="Head", sensation="Throbbing")
    db_session.add(headache)
    db_session.flush()
    db_session.add_all(
        [
            SymptomLog(
                username=authenticated_user["username"], symptom_id=headache.id, intensity=8, timestamp=hours_ago(3)
            ),
            SymptomLog(
                username=authenticated_user["username"], symptom_id=headache.id, intensity=9, timestamp=hours_ago(100)
            ),
        ]
    )
    db_session.flush()
    # Act
    status = SymptomLogService().get_washout_status(db_session, NOW)
    # Assert
    assert status.active is True
    assert status.ends_at == hours_ago(3) + timedelta(hours=48)


def test_get_washout_status_without_logs_is_inactive(db_session, authenticated_user):
    # Act
    status = SymptomLogService().get_washout_status(db_session, NOW)
    # Assert
    assert status.active is False


ALLERGY_MESSAGE = "If you have swelling of your lips, tongue or throat, or trouble breathing, get emergency care now."
# FDA Big 9 allergens plus common trigger foods; a safety message must never point at a food
FOOD_WORDS = ["milk", "dairy", "egg", "fish", "shellfish", "nut", "peanut", "wheat", "gluten", "soy", "sesame"]


@pytest.fixture
def make_symptom(db_session, authenticated_user):
    def make(location: str, sensation: str) -> Symptom:
        symptom = Symptom(
            username=authenticated_user["username"],
            name=f"{sensation} {location}",
            location=location,
            sensation=sensation,
        )
        db_session.add(symptom)
        db_session.flush()
        return symptom

    return make


def post_log(test_client, symptom: Symptom, intensity: int = 5):
    return test_client.post(
        "/symptom-logs/",
        json={"symptom_id": str(symptom.id), "intensity": intensity, "timestamp": "2026-10-25T10:00:00Z"},
    )


@pytest.mark.parametrize(
    ("location", "sensation", "family", "route", "message"),
    [
        ("Throat", "Swelling", None, "allergy_like", ALLERGY_MESSAGE),
        ("Abdomen", "Bloating", "gi", "model", None),
    ],
)
def test_post_returns_computed_route(test_client, make_symptom, location, sensation, family, route, message):
    # Arrange
    symptom = make_symptom(location, sensation)
    # Act
    response = post_log(test_client, symptom)
    # Assert
    assert response.status_code == 201
    body = response.json()
    assert (body["family"], body["route"], body["safety_message"]) == (family, route, message)


def test_post_red_flag_returns_seek_care_message(test_client, make_symptom):
    # Arrange
    symptom = make_symptom("Chest", "Pain")
    # Act
    body = post_log(test_client, symptom).json()
    # Assert
    assert body["route"] == "red_flag"
    assert body["family"] is None
    assert "medical care" in body["safety_message"]


def test_get_my_logs_returns_computed_route(test_client, make_symptom):
    # Arrange
    post_log(test_client, make_symptom("Head", "Throbbing"))
    post_log(test_client, make_symptom("Knees", "Bleeding"))
    # Act
    response = test_client.get("/symptom-logs/user/me")
    # Assert
    assert response.status_code == 200
    routes = {(log["route"], log["family"]) for log in response.json()}
    assert routes == {("model", "head"), ("red_flag", None)}


def test_route_is_not_stored():
    # Act
    columns = {c.key for c in inspect(SymptomLog).columns}
    # Assert
    assert columns.isdisjoint({"family", "route", "safety_message"})


@pytest.mark.parametrize("route", ["red_flag", "allergy_like"])
def test_safety_messages_never_name_a_food(route):
    # Act
    message = get_routing()["safety_messages"][route].lower()
    # Assert
    assert not [word for word in FOOD_WORDS if word in message]
