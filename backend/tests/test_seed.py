from sqlalchemy import func, select

import pytest

from app.models import Order, User
from app.seed import ADMIN_EMAIL, SAMPLE_ORDERS, seed, seed_users
from app.security import verify_password


def _count(db) -> int:
    return db.scalar(select(func.count()).select_from(Order))


def test_seed_adds_sample_orders(empty_db):
    seed(empty_db)
    assert _count(empty_db) == len(SAMPLE_ORDERS)


def test_seed_is_idempotent(empty_db):
    seed(empty_db)
    seed(empty_db)
    assert _count(empty_db) == len(SAMPLE_ORDERS)


def test_seed_users_creates_admin_and_customers(empty_db):
    created = seed_users(empty_db, "demo-pass", "dev")
    assert created == len({o["customer_email"] for o in SAMPLE_ORDERS}) + 1
    admin = empty_db.scalar(select(User).where(User.email == ADMIN_EMAIL))
    assert admin.role == "admin"
    assert verify_password("demo-pass", admin.hashed_password)


def test_seed_users_is_idempotent(empty_db):
    seed_users(empty_db, "demo-pass", "dev")
    assert seed_users(empty_db, "demo-pass", "dev") == 0


@pytest.mark.parametrize("password, env", [("", "dev"), ("demo-pass", "prod")])
def test_seed_users_skipped_without_password_or_in_prod(empty_db, password, env):
    assert seed_users(empty_db, password, env) == 0
