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
@pytest.mark.parametrize(
    ("days_ago", "expected_eligible"),
    [
        (3, True),
        (14, True),
        (15, False),
    ],
)
def test_return_window_boundaries(days_ago, expected_eligible):
    result = check_return_eligibility(make_order(days_ago), now=NOW, window_days=14)
    assert result["eligible"] is expected_eligible


def test_days_since_delivery_is_reported():
    result = check_return_eligibility(make_order(3), now=NOW, window_days=14)
    assert result["days_since_delivery"] == 3


def test_reason_mentions_days_over_window():
    result = check_return_eligibility(make_order(15), now=NOW, window_days=14)
    assert "by 1 day" in result["reason"]


def test_not_delivered_is_not_eligible():
    result = check_return_eligibility(make_order(None), now=NOW, window_days=14)
    assert result["eligible"] is False
    assert result["days_since_delivery"] is None


def test_custom_window_changes_outcome():
    assert check_return_eligibility(make_order(18), now=NOW, window_days=14)["eligible"] is False
    assert check_return_eligibility(make_order(21), now=NOW, window_days=21)["eligible"] is True


# ------------ decide_refund_approval ----------
@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (29.90, "auto_approved"),
        (100.00, "auto_approved"),
        (100.01, "pending"),
        (219, "pending"),
    ],
)
def test_refund_approval(amount, expected):
    assert decide_refund_approval(amount, CEILING) == expected


@pytest.mark.parametrize("amount", [0, -219])
def test_non_positive_refund_is_rejected(amount):
    with pytest.raises(ValueError):
        decide_refund_approval(amount, CEILING)


def test_ceiling_is_configurable():
    assert decide_refund_approval(150, ceiling_eur=200) == "auto_approved"
