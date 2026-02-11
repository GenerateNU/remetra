"""
Pytest configuration and shared fixtures.

pytest automatically loads this file and makes fixtures available
to all test files without needing imports!

Fixtures: Reusable test setup code (test data, database connections, auth tokens)
Define once here, use in any test by adding the fixture name as a function parameter makes life sm easier

Common use cases (Most likely what we'll do):
- Database sessions for tests
- Authenticated users and auth tokens
- Mock external API responses
- Standard test data that multiple tests need
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.food import Food
from models.food_log import FoodLog
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from models.user import User

__all__ = ["User", "Symptom", "SymptomLog", "Food", "FoodLog"]

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://test_user:test_password@test-db:5432/test_remetra")
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """
    Create database engine for the entire test session.

    Creates all tables at start, drops them at end.
    Scope='session' means this runs once for all tests.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after all tests complete
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Provide a test database session for each test.

    Each test gets a fresh transaction that's rolled back after the test.
    This ensures tests don't interfere with each other.

    Scope='function' means each test gets its own session.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.

    Any test can use this by adding 'sample_user_data' as a parameter.
    Keeps test data consistent across all tests.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "dob": "2000-01-01",
        "disease": ["lupus"],
        "weight": 150.0,
    }


@pytest.fixture
def authenticated_user(db_session, sample_user_data):
    """
    Create and return an authenticated user with token.

    Useful for tests that need a logged-in user.
    Returns dict with user and access_token.
    """
    from schemas.user import UserCreate
    from services.auth_service import AuthService

    service = AuthService()

    user_create = UserCreate(**sample_user_data)
    user = service.register_user(db_session, user_create)

    token_data = service.authenticate_user(db_session, sample_user_data["username"], sample_user_data["password"])

    return {"user": user, "token": token_data["access_token"], "username": user.username}


@pytest.fixture
def sample_food_data():
    """
    Sample food data for testing.

    Any test can use this by adding 'sample_food_data' as a parameter.
    """
    return {
        "name": "test pizza",
        "ingredients": list(["flour", "cheese", "tomato"]),
        "username": "test user",
    }


@pytest.fixture
def multiple_foods_data():
    """ "
    Sample data for multiple food items.

    Any test can use this by adding 'multiple_foods_data' as a parameter.
    """

    return [
        {"name": "test pizza", "ingredients": ["flour", "cheese", "tomato"], "username": "test user"},
        {"name": "test salad", "ingredients": ["lettuce", "tomato", "cucumber"], "username": "test user"},
        {"name": "test sandwich", "ingredients": ["bread", "ham", "cheese"], "username": "test user"},
    ]
