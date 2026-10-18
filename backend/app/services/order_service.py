from datetime import datetime

from app.agent.business import check_return_eligibility
from app.models import Order
from app.repositories.order_repository import OrderRepository

class OrderNotFoundError(Exception):
    """Raised when no order matches the given ID."""

    def __init__(self, order_id: str) -> None:
        super().__init__(f"Order {order_id} not found")
        self.order_id = order_id


class OrderService:
    def __init__(self, repo: OrderRepository, window_days: int) -> None:
        self.repo = repo
        self.window_days = window_days

    def list_orders(self) -> list[Order]:
        """List all orders"""
        return list(self.repo.list_all())

    def get_order(self, order_id: str) -> Order:
        normalized_id = order_id.upper().strip()
        order = self.repo.get_by_id(normalized_id)
        if order is None:
            raise OrderNotFoundError(normalized_id)
        return order

    def check_return(self, order_id: str, now: datetime | None = None) -> dict:
        order = self.get_order(order_id)
        return check_return_eligibility(
            {
                "id": order.id,
                "status": order.status,
                "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
            },
            now=now,
            window_days=self.window_days,
        )
