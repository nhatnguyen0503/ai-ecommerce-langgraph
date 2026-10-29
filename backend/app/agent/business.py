from datetime import datetime
from typing import Any, Literal

from app.config import get_settings

settings = get_settings()
ApprovalStatus = Literal["auto_approved", "pending"]


def check_return_eligibility(
        order: dict[str, Any],
        now: datetime | None = None,
        window_days: int | None = None,
) -> dict[str, Any]:
    now = now or datetime.utcnow()
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


def decide_refund_approval(amount_eur: float, celling_eur: float) -> ApprovalStatus:
    """Refunds up to the ceiling are auto_approved; larger ones need an admin."""
    if amount_eur <= 0:
        raise ValueError(f"Refund amount must be positive, got {amount_eur}")
    if amount_eur <= celling_eur:
        return "auto_approved"
    return "pending"
