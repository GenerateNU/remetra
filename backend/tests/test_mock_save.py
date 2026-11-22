"""Saving mock users: per-user rows, re-runs replace, failures leave nothing half-written, clear spares real users."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from sqlalchemy import func, select

import scripts.mock_users.save as save_module
from auth_context import system_access
from models.daily_health_metrics import DailyHealthMetrics
from models.food import Food
from models.food_log import FoodLog
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from models.user import User
from scripts.mock_users.clear import main as clear_main
from scripts.mock_users.generate import generate_users
from scripts.mock_users.health import TIMEZONE
from scripts.mock_users.save import clear_mock_users, save_users, symptom_name

END = date(2026, 11, 1)
OWNED = [Food, FoodLog, Symptom, SymptomLog, DailyHealthMetrics]


def _is_mock(model):
    return model.username.startswith("mock_", autoescape=True)


def _mock_usernames(db):
    return set(db.scalars(select(User.username).where(_is_mock(User))))


def _mock_row_counts(db):
    with system_access():
        return {m.__tablename__: db.scalar(select(func.count()).select_from(m).where(_is_mock(m))) for m in OWNED}


@pytest.fixture
def real_user(db_session):
    db_session.add(User(username="casey", email="casey@example.com"))
    db_session.flush()
    db_session.add(Food(name="Toast", ingredients=["wheat bread"], username="casey"))
    db_session.commit()


def _real_user_intact(db):
    with system_access():
        foods = db.scalars(select(Food.name).where(Food.username == "casey")).all()
    return db.get(User, "casey") is not None and foods == ["Toast"]


def test_each_user_gets_their_own_rows(db_session):
    users = generate_users(3, 4, END, days=8)

    save_users(db_session, users)

    with system_access():
        for user in users:
            foods = db_session.scalars(select(Food).where(Food.username == user.username)).all()
            assert {f.name for f in foods} == {f.name for f in user.foods}
            logs = db_session.scalars(select(FoodLog).where(FoodLog.username == user.username)).all()
            assert len(logs) == len(user.meals)
            assert {log.food_id for log in logs} <= {f.id for f in foods}

            symptoms = db_session.scalars(select(Symptom).where(Symptom.username == user.username)).all()
            assert {(s.sensation, s.location) for s in symptoms} == {
                (e.symptom.sensation, e.symptom.location) for e in user.symptoms
            }
            assert all(s.name == symptom_name(s.sensation, s.location) for s in symptoms)
            symptom_logs = db_session.scalars(select(SymptomLog).where(SymptomLog.username == user.username)).all()
            assert len(symptom_logs) == len(user.symptoms)

            health = db_session.scalars(
                select(DailyHealthMetrics).where(DailyHealthMetrics.username == user.username)
            ).all()
            assert {row.date for row in health} == {day.date for day in user.health_days}
            assert {row.timezone for row in health} == {TIMEZONE}


def test_rerun_replaces_instead_of_duplicating(db_session):
    users = generate_users(1, 3, END, days=6)
    save_users(db_session, users)
    first = _mock_row_counts(db_session)

    save_users(db_session, users)

    assert _mock_row_counts(db_session) == first
    assert _mock_usernames(db_session) == {"mock_001", "mock_002", "mock_003"}
    assert first["foods"] == sum(len(u.foods) for u in users)


def test_rerun_with_fewer_users_drops_the_extras(db_session):
    save_users(db_session, generate_users(1, 3, END, days=4))

    save_users(db_session, generate_users(1, 1, END, days=4))

    assert _mock_usernames(db_session) == {"mock_001"}


def test_saving_zero_users_removes_existing_mock_users(db_session):
    save_users(db_session, generate_users(1, 2, END, days=3))

    save_users(db_session, [])

    assert _mock_usernames(db_session) == set()


def test_failed_rerun_keeps_previous_mock_users(db_session, real_user, monkeypatch):
    first = generate_users(1, 2, END, days=5)
    save_users(db_session, first)
    before = _mock_row_counts(db_session)
    real_insert = save_module.pg_insert
    calls = []

    def insert_that_fails_on_third_table(model):
        calls.append(model)
        if len(calls) == 3:
            raise RuntimeError("insert failed")
        return real_insert(model)

    monkeypatch.setattr(save_module, "pg_insert", insert_that_fails_on_third_table)
    with pytest.raises(RuntimeError, match="insert failed"):
        save_users(db_session, generate_users(9, 4, END, days=5))

    assert _mock_usernames(db_session) == {u.username for u in first}
    assert _mock_row_counts(db_session) == before
    assert _real_user_intact(db_session)


def test_failed_first_run_leaves_no_mock_users(db_session, real_user, monkeypatch):
    monkeypatch.setattr(save_module, "pg_insert", MagicMock(side_effect=RuntimeError("insert failed")))

    with pytest.raises(RuntimeError, match="insert failed"):
        save_users(db_session, generate_users(1, 2, END, days=4))

    assert _mock_usernames(db_session) == set()
    assert _real_user_intact(db_session)


def test_clear_leaves_real_users_alone(db_session, real_user):
    db_session.add(User(username="mockXreal", email="decoy@example.com"))  # `_` must not act as a LIKE wildcard
    db_session.commit()
    save_users(db_session, generate_users(1, 2, END, days=4))

    removed = clear_mock_users(db_session)

    assert removed == 2
    assert _mock_usernames(db_session) == set()
    assert set(_mock_row_counts(db_session).values()) == {0}
    assert db_session.get(User, "mockXreal") is not None
    assert _real_user_intact(db_session)


def test_clear_main_reports_how_many_were_removed(capsys, monkeypatch):
    monkeypatch.setattr("scripts.mock_users.clear.clear_mock_users", lambda db: 3)
    monkeypatch.setattr("scripts.mock_users.clear.SessionLocal", MagicMock)

    clear_main()

    assert "Removed 3 mock users" in capsys.readouterr().out
