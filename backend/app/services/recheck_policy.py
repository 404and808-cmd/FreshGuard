
from datetime import datetime, timedelta, timezone


# Prototype defaults: how often to recheck claims.
RECHECK_INTERVALS = {
    "low": timedelta(days=30),
    "medium": timedelta(days=7),
    "high": timedelta(hours=24),
}


def calculate_next_check(
    volatility: str,
    checked_at: datetime | None = None,
) -> datetime:
    """
    Calculate the next verification time for a claim.
    """

    if volatility not in RECHECK_INTERVALS:
        raise ValueError(f"Unknown volatility level: {volatility}")

    if checked_at is None:
        checked_at = datetime.now(timezone.utc)

    # Treat naive timestamps as UTC.
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=timezone.utc)

    return checked_at + RECHECK_INTERVALS[volatility]


def is_recheck_due(
    volatility: str,
    checked_at: datetime,
    now: datetime | None = None,
) -> bool:
    """
    Return True when the claim has reached its next check time.
    """

    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    next_check = calculate_next_check(volatility, checked_at)

    return now >= next_check
