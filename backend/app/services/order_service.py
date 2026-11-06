import logging
from datetime import datetime

from app.agent.business import check_return_eligibility
from app.models import Order, User
from app.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)


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
        logger.debug("Debug %s", normalized_id)
        order = self.repo.get_by_id(normalized_id)
        if order is None:
            logger.info("Order not found: %s", normalized_id)
            raise OrderNotFoundError(normalized_id)
        return order

    def get_order_for(self, order_id: str, viewer: User) -> Order:
        """Like get_order, but customers may only see their own orders.

        Someone else's order raises the SAME OrderNotFoundError as a missing one,
        so order ids cannot be probed.
        """
        order = self.get_order(order_id)
        if viewer.role != "admin" and order.user_id != viewer.id:
            logger.info("Order %s hidden from user_id=%s", order.id, viewer.id)
            raise OrderNotFoundError(order.id)
        return order

    def get_return_eligibility(self, order_id: str, now: datetime | None = None, viewer: User | None = None) -> dict:
        order = self.get_order_for(order_id, viewer) if viewer else self.get_order(order_id)
        result = check_return_eligibility(
            {
                "id": order.id,
                "status": order.status,
                "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
            },
            now=now,
            window_days=self.window_days,
        )

        logger.info(
            "Return eligibility for %s: eligible=%s, days_since_delivery=%s",
            order.id, result["eligible"], result["days_since_delivery"],
        )
        return result
