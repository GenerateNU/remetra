"""Test that every route except health checks requires authentication."""

from routers.auth import get_current_user
from main import app

def route_requires_auth(route):
    for dependency in route.dependant.dependencies:
        if dependency.call is get_current_user:
            return True
    return False


def test_all_auth_routes_except_health():
    exempt_paths = {'/health', '/auth/signup', '/auth/login', '/scalar', '/'}
    unprotected = []

    for route in app.routes:
        if not hasattr(route, 'dependant'):
            continue
        if route.path in exempt_paths:
            continue
        if not route_requires_auth(route):
            unprotected.append(route.path)

    assert not unprotected, f"These routes don't require auth: {unprotected}"