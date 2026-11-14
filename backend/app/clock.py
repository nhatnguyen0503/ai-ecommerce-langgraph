from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """Current UTC time WITHOUT tzinfo.

    The order date columns are stored without a time zone (naive, UTC by convention),
    and Python cannot subtract a naive datetime from an aware one. This helper keeps
    the "naive UTC" convention in one place without the deprecated datetime.utcnow().

    Remove it once the date columns are migrated to timestamptz and the code uses
    datetime.now(timezone.utc) everywhere.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
