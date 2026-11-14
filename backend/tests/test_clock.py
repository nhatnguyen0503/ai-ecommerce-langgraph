from datetime import UTC, datetime, timedelta

from app.clock import utc_now_naive


def test_utc_now_naive_has_no_timezone():
    assert utc_now_naive().tzinfo is None


def test_utc_now_naive_is_current_utc_time():
    expected = datetime.now(UTC).replace(tzinfo=None)
    assert abs(utc_now_naive() - expected) < timedelta(seconds=1)
