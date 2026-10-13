"""Deterministic business logic used by the graph nodes: order lookup and the
Finnish 14-day return-window eligibility check. Kept separate from the graph
so it can be unit-tested without any LLM involved.
"""
from datetime import datetime
from typing import Any, Optional

from app_reference.config import get_settings
from app_reference.database import SessionLocal
from app_reference.models import Order

settings = get_settings()


def find_order(order_id: str) -> Optional[dict[str, Any]]:
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id.strip().upper()).first()
        if not order:
            return None
        return {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "items": order.items,
            "total_amount": order.total_amount,
            "currency": order.currency,
            "status": order.status,
            "warehouse": order.warehouse,
            "order_date": order.order_date.isoformat(),
            "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
        }
    finally:
        db.close()


def check_return_eligibility(order: dict[str, Any]) -> dict[str, Any]:
    """Applies Finland's 14-day consumer return window, counted from delivery."""
    if not order.get("delivered_date"):
        return {
            "eligible": False,
            "days_since_delivery": None,
            "reason": f"Order {order['id']} has not been delivered yet (current status: {order['status']}), "
            "so the return window hasn't started.",
        }

    delivered = datetime.fromisoformat(order["delivered_date"])
    days_since = (datetime.utcnow() - delivered).days
    window = settings.return_window_days
    eligible = days_since <= window

    if eligible:
        reason = f"Delivered {days_since} day(s) ago, within the {window}-day Finnish return window."
    else:
        reason = (
            f"Delivered {days_since} day(s) ago, which is past the {window}-day Finnish return window "
            f"(exceeded by {days_since - window} day(s))."
        )

    return {"eligible": eligible, "days_since_delivery": days_since, "reason": reason}
