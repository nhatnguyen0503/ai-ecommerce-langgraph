from datetime import datetime, timedelta

import pytest

from app.models import Order
from app.services.order_service import OrderService, OrderNotFoundError

NOW = datetime(2026, 10, 10, 12, 0, 0)

class FakeOrderRepository:
    def __init__(self, orders: list[Order]) -> None:
        self.orders = {o.id: o for o in orders}

    def get_by_id(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)

    def list_all(self) -> list[Order]:
        return list(self.orders.values())

def make_order(order_id: str, delivered_days_ago: int | None) -> Order:
    delivered = None if delivered_days_ago is None else NOW - timedelta(days=delivered_days_ago)
    return Order(id=order_id, status="delivered" if delivered else "in_transit", delivered_date=delivered)


@pytest.fixture
def service() -> OrderService:
    repo = FakeOrderRepository([make_order("FI-1", 3), make_order("FI-2", 20)])
    return OrderService(repo, window_days=14)

def test_get_order_normalizes_id(service):
    order = service.get_order("  fi-1 ")
    assert order.id == "FI-1"

def test_get_order_missing_raises(service):
    with pytest.raises(OrderNotFoundError):
        service.get_order("FI-404")

def test_check_return_within_window(service):
    result = service.check_return("FI-1", now=NOW)
    assert result["eligible"] is True


def test_check_return_past_window(service):
    result = service.check_return("FI-2", now=NOW)
    assert result["eligible"] is False
