from datetime import datetime, timedelta

import pytest

from app.agent.business import check_return_eligibility, decide_refund_approval

NOW = datetime(2026, 10, 10, 12, 0, 0)
CEILING = 100.0


def make_order(delivery_days_ago):
    delivered = None if delivery_days_ago is None else (NOW - timedelta(days=delivery_days_ago)).isoformat()
    return {
        "id": "FI-TEST",
        "status": "delivered" if delivered else "in_transit",
        "delivered_date": delivered,
    }


# ------------ check_return_eligibility ----------

def test_delivered_recently_is_eligible():
    result = check_return_eligibility(make_order(3), now=NOW, window_days=14)
    assert result["eligible"] is True
    assert result["days_since_delivery"] == 3


def test_exactly_14_days_is_still_eligible():
    result = check_return_eligibility(make_order(14), now=NOW, window_days=14)
    assert result["eligible"] is True


def test_15_days_is_not_eligible():
    result = check_return_eligibility(make_order(15), now=NOW, window_days=14)
    assert result["eligible"] is False
    assert "by 1 day" in result["reason"]


def test_not_delivered_is_not_eligible():
    result = check_return_eligibility(make_order(None), now=NOW, window_days=14)
    assert result["eligible"] is False
    assert result["days_since_delivery"] is None


def test_custom_window_changes_outcome():
    assert check_return_eligibility(make_order(18), now=NOW, window_days=14)["eligible"] is False
    assert check_return_eligibility(make_order(21), now=NOW, window_days=21)["eligible"] is True


# Test decide refund approval
def test_small_refund_is_auto_approval():
    assert decide_refund_approval(29.90, CEILING) == "auto_approved"


def test_refund_exactly_at_ceiling_is_auto_approved():
    assert decide_refund_approval(100, CEILING) == "auto_approved"


def test_refund_just_over_ceiling_needs_admin():
    assert decide_refund_approval(100.01, CEILING) == "pending"


def test_large_refund_needs_admin():
    assert decide_refund_approval(219.00, CEILING) == "pending"


def test_non_positive_refund_is_rejected():
    with pytest.raises(ValueError):
        decide_refund_approval(0, CEILING)
    with pytest.raises(ValueError):
        decide_refund_approval(-219, CEILING)


def test_ceiling_is_configurable():
    assert decide_refund_approval(150, ceiling_eur=200) == "auto_approved"
