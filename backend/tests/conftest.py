import os

# Tests must not depend on the developer's .env; set a fixed dummy secret first.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-" + "x" * 32)

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies import login_limiter
from app.main import app
from app.models import Order, User
from app.security import create_access_token

NOW = datetime(2026, 10, 10, 12, 0, 0)


@pytest.fixture
def db(empty_db):
    """The same database, with one delivered order (FI-10234)."""
    empty_db.add(
        Order(
            id="FI-10234",
            customer_name="Aino",
            customer_email="aino@example.fi",
            items=[{"name": "Wool Beanie", "qty": 1, "price": 29.90}],
            total_amount=29.90,
            status="delivered",
            order_date=NOW - timedelta(days=5),
            delivered_date=NOW - timedelta(days=3),
        )
    )
    empty_db.commit()
    return empty_db


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def empty_db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _make_user(db, email: str, role: str) -> User:
    user = User(email=email, hashed_password="not-used-in-api-tests", role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _headers(user: User) -> dict[str, str]:
    token = create_access_token(subject=str(user.id), role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db) -> User:
    return _make_user(db, "admin@test.fi", "admin")


@pytest.fixture
def owner(db) -> User:
    """Customer who owns FI-10234."""
    user = _make_user(db, "owner@test.fi", "customer")
    db.get(Order, "FI-10234").user_id = user.id
    db.commit()
    return user


@pytest.fixture
def other_customer(db) -> User:
    return _make_user(db, "other@test.fi", "customer")


@pytest.fixture
def admin_headers(admin_user) -> dict[str, str]:
    return _headers(admin_user)


@pytest.fixture
def owner_headers(owner) -> dict[str, str]:
    return _headers(owner)


@pytest.fixture
def other_headers(other_customer) -> dict[str, str]:
    return _headers(other_customer)


@pytest.fixture(autouse=True)
def _reset_login_limiter():
    login_limiter.reset()
    yield
