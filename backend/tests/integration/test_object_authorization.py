"""A signed-in user can only see and change their own rows."""

from datetime import date

from auth_context import current_username, system_access
from main import app
from models.daily_health_metrics import DailyHealthMetrics
from models.food import Food
from repositories.health_repository import HealthRepository
from repositories.user_repository import UserRepository
from routers.auth import get_current_user
from schemas.health import HealthDayEntry
from schemas.user import UserResponse


def test_user_cannot_read_or_change_another_users_records(db_session, test_client):
    """User B gets 404 for user A's rows, and cannot choose the owner of a new row."""
    repo = UserRepository()
    alice = repo.create(
        db=db_session,
        username="alice",
        email="alice@example.com",
        clerk_user_id="user_alice",
    )
    bob = repo.create(
        db=db_session,
        username="bob",
        email="bob@example.com",
        clerk_user_id="user_bob",
    )
    profiles = {
        "alice": UserResponse.model_validate(alice),
        "bob": UserResponse.model_validate(bob),
    }
    acting_as = {"name": "alice"}

    async def override_current_user():
        token = current_username.set(acting_as["name"])
        try:
            yield profiles[acting_as["name"]]
        finally:
            current_username.reset(token)

    def sign_in(name: str) -> None:
        acting_as["name"] = name

    app.dependency_overrides[get_current_user] = override_current_user
    try:
        sign_in("alice")
        food = test_client.post(
            "/food/",
            json={"name": "alice soup", "ingredients": ["gluten"], "username": "bob"},
        )
        assert food.status_code == 201, food.text
        assert food.json()["username"] == "alice"
        food_id = food.json()["id"]

        tag = test_client.post("/tags", json={"name": "alice-gluten"})
        assert tag.status_code == 201, tag.text
        tag_id = tag.json()["id"]
        attached = test_client.post(f"/food/{food_id}/tags", json={"tag_ids": [tag_id]})
        assert attached.status_code == 201, attached.text

        symptom = test_client.post(
            "/symptom/",
            json={"name": "headache", "location": "jaw", "sensation": "ache", "username": "bob"},
        )
        assert symptom.status_code == 201, symptom.text
        assert symptom.json()["username"] == "alice"
        symptom_id = symptom.json()["id"]

        food_log = test_client.post(
            "/food-log/",
            json={
                "food_id": food_id,
                "timestamp": "2024-01-01T08:00:00Z",
                "username": "bob",
            },
        )
        assert food_log.status_code == 201, food_log.text
        assert food_log.json()["username"] == "alice"
        food_log_id = food_log.json()["id"]

        symptom_log = test_client.post(
            "/symptom-logs/",
            json={
                "symptom_id": symptom_id,
                "intensity": 6,
                "timestamp": "2024-01-01T10:00:00Z",
                "username": "bob",
            },
        )
        assert symptom_log.status_code == 201, symptom_log.text
        assert symptom_log.json()["username"] == "alice"
        symptom_log_id = symptom_log.json()["id"]

        sign_in("bob")
        bob_reads = [
            test_client.get(f"/food/{food_id}"),
            test_client.put(f"/food/{food_id}", json={"name": "stolen", "ingredients": ["nope"]}),
            test_client.delete(f"/food/{food_id}"),
            test_client.get(f"/food/{food_id}/tags"),
            test_client.post(f"/food/{food_id}/tags", json={"tag_ids": [tag_id]}),
            test_client.get(f"/symptom/{symptom_id}"),
            test_client.put(
                f"/symptom/{symptom_id}",
                json={"name": "stolen", "location": "arm", "sensation": "burn"},
            ),
            test_client.delete(f"/symptom/{symptom_id}"),
            test_client.get(f"/food-log/{food_log_id}"),
            test_client.put(f"/food-log/{food_log_id}", json={"notes": "stolen"}),
            test_client.delete(f"/food-log/{food_log_id}"),
            test_client.get(f"/symptom-logs/{symptom_log_id}"),
            test_client.put(f"/symptom-logs/{symptom_log_id}", json={"intensity": 1}),
            test_client.delete(f"/symptom-logs/{symptom_log_id}"),
        ]
        assert [response.status_code for response in bob_reads] == [404] * len(bob_reads)

        assert all(row["id"] != food_id for row in test_client.get("/food/").json())
        assert all(row["id"] != symptom_id for row in test_client.get("/symptom/").json())
        assert all(row["id"] != food_log_id for row in test_client.get("/food-log/user/me").json())
        assert all(row["id"] != symptom_log_id for row in test_client.get("/symptom-logs/user/me").json())

        stolen_run = test_client.post(
            "/algorithm/run",
            json={"user_id": "alice", "time_window_hours": 4},
        )
        assert stolen_run.status_code == 200, stolen_run.text
        assert stolen_run.json()["associations"] == []
        assert test_client.get("/algorithm/user/alice").status_code == 404

        sign_in("alice")
        own_run = test_client.post("/algorithm/run", json={"time_window_hours": 4})
        assert own_run.status_code == 200, own_run.text
        assert own_run.json()["associations"]
        assert all(row["user_id"] == "alice" for row in own_run.json()["associations"])

        sign_in("bob")
        assert test_client.get("/algorithm/associations").json() == []

        sign_in("alice")
        assert test_client.get(f"/food/{food_id}").json()["name"] == "alice soup"
        assert [row["name"] for row in test_client.get(f"/food/{food_id}/tags").json()] == ["alice-gluten"]
        assert test_client.get("/algorithm/associations").json()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_query_with_no_user_returns_no_rows(db_session):
    """Owned rows stay hidden until a user is set. system_access() can still see them."""
    UserRepository().create(
        db=db_session,
        username="carol",
        email="carol@example.com",
        clerk_user_id="user_carol",
    )
    token = current_username.set("carol")
    try:
        food = Food(name="carol soup", ingredients=["salt"], username="carol")
        db_session.add(food)
        db_session.flush()
        food_id = food.id
    finally:
        current_username.reset(token)

    assert current_username.get() is None
    db_session.expire_all()
    assert db_session.query(Food).filter(Food.id == food_id).all() == []

    with system_access():
        visible = db_session.query(Food).filter(Food.id == food_id).one()
        assert visible.name == "carol soup"


def test_user_cannot_read_another_users_health_data(db_session):
    """User B can never see user A's health days"""
    repo = UserRepository()
    repo.create(db=db_session, username="alice", email="alice@example.com", clerk_user_id="user_alice")
    repo.create(db=db_session, username="bob", email="bob@example.com", clerk_user_id="user_bob")

    HealthRepository().save_days(
        db_session, "alice", "America/New_York", [HealthDayEntry(date=date(2026, 10, 20), sleep_total_min=420)]
    )

    token = current_username.set("bob")
    try:
        db_session.expire_all()
        assert db_session.query(DailyHealthMetrics).all() == []
    finally:
        current_username.reset(token)

    token = current_username.set("alice")
    try:
        assert len(db_session.query(DailyHealthMetrics).all()) == 1
    finally:
        current_username.reset(token)