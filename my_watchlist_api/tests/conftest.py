"""
Shared pytest fixtures for the test suite.

Uses an in-memory SQLite database so tests are fast, isolated, and never
touch the real my_watchlist.db file.
"""
import os

# Must be set before any app module is imported so pydantic-settings picks
# up SQLite instead of the real PostgreSQL URL from .env
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db

# ── import every model so SQLAlchemy registers them before create_all ──────────
from app.models.user import User           # noqa: F401
from app.models.group import Group         # noqa: F401
from app.models.user_group import UserGroup  # noqa: F401
from app.models.group_request import GroupRequest  # noqa: F401
from app.models.watchlist import Watchlist   # noqa: F401
from app.models.movie import Movie           # noqa: F401
from app.models.viewing import Viewing       # noqa: F401
from app.models.watchlist_movie import watchlist_movie_table  # noqa: F401

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Single in-memory engine shared for the whole test session."""
    _engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture()
def db(engine):
    """
    Each test gets its own connection + transaction rolled back at teardown,
    keeping tests isolated without recreating tables.
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestingSession = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    """Return a FastAPI TestClient wired to the test DB."""
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ── helper factories ───────────────────────────────────────────────────────────

def make_user(db, username="testuser", email="test@example.com", password="secret123"):
    """Create and persist a User with a hashed password."""
    from app.core.security import hash_password

    user = User(
        username=username,
        firstName="Test",
        lastName="User",
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_group(db, creator, name="Test Group", other_members=None, public=True):
    """Create and persist a Group with *creator* as admin."""
    if other_members is None:
        other_members = []
    from app.models.user_group import UserGroup

    group = Group(name=name, description="A test group", public=public)
    user_group = UserGroup(user=creator, admin=1)

    for member in other_members:
        other_user_group = UserGroup(user=member, admin=0)
        group.user_groups.append(other_user_group)

    group.user_groups.append(user_group)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def auth_headers(client, username="testuser", password="secret123"):
    """Log in and return Bearer auth headers."""
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.json()
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

