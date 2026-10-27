from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import Order
from app.main import app

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
