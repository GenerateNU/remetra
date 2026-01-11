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

import pytest

# Example: In a real app, you'd have fixtures like these
# @pytest.fixture
# def db_session():
#     """Provide a test database session."""
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@pytest.fixture
def sample_user_data():
    """
    Example fixture providing test user data.

    Any test can use this by adding 'sample_user_data' as a parameter.
    Keeps test data consistent across all tests.
    """
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User",
    }
