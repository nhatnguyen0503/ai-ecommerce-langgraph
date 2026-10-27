from sqlalchemy import func, select

from app.models import Order
from app.seed import SAMPLE_ORDERS, seed


def _count(db) -> int:
    return db.scalar(select(func.count()).select_from(Order))


def test_seed_adds_sample_orders(empty_db):
    seed(empty_db)
    assert _count(empty_db) == len(SAMPLE_ORDERS)


def test_seed_is_idempotent(empty_db):
    seed(empty_db)
    seed(empty_db)
    assert _count(empty_db) == len(SAMPLE_ORDERS)
