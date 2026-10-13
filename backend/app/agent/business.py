from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.config import get_settings

from app.models import Order


settings = get_settings()

def find_order(db: Session, order_id: str) -> Optional[dict[str, Any]]:
    """Check order and return order by dict type, if not return None"""
    normalized_id = order_id.strip().upper()
    order = db.query(Order).filter(Order.id == normalized_id).first()
    if order is None:
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

def check_return_eligibility(
        order: dict[str, Any],
        now: Optional[datetime] = None,
        window_days: Optional[int] = None,
)-> dict[str, Any]:
    now  = now or datetime.utcnow()
    window = window_days if window_days is not None else settings.return_window_days

    if not order.get("delivered_date"):
        return {
            "eligible": False,
            "days_since_delivery": None,
            "reason": f"Order {order['id']} did not delivered(status: {order['status']}), "
                      "so cant calculate return eligibility ",
        }
    delivered = datetime.fromisoformat(order["delivered_date"])
    days_since = (now - delivered).days
    eligible = days_since <= window

    if eligible:
        reason = f"Delivered {days_since} day(s) ago, within the {window}-day return window."
    else:
        reason = (f"Delivered {days_since} day(s) ago, past the {window}-day return window "
                  f"by {days_since - window} day(s).")
    return {"eligible": eligible, "days_since_delivery": days_since, "reason": reason}

