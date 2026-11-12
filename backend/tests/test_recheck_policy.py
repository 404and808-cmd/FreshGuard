
from datetime import datetime, timedelta, timezone

import pytest

from app.services.recheck_policy import (
    calculate_next_check,
    is_recheck_due,
)


def test_high_volatility_rechecks_after_24_hours():
    checked_at = datetime(2026, 11, 1, tzinfo=timezone.utc)

    result = calculate_next_check("high", checked_at)

    assert result == checked_at + timedelta(hours=24)


def test_medium_volatility_rechecks_after_7_days():
    checked_at = datetime(2026, 11, 1, tzinfo=timezone.utc)

    result = calculate_next_check("medium", checked_at)

    assert result == checked_at + timedelta(days=7)


def test_low_volatility_rechecks_after_30_days():
    checked_at = datetime(2026, 11, 1, tzinfo=timezone.utc)

    result = calculate_next_check("low", checked_at)

    assert result == checked_at + timedelta(days=30)


def test_recheck_is_not_due_before_deadline():
    checked_at = datetime(2026, 11, 1, tzinfo=timezone.utc)
    now = checked_at + timedelta(hours=23)

    assert is_recheck_due("high", checked_at, now) is False


def test_recheck_is_due_at_deadline():
    checked_at = datetime(2026, 11, 1, tzinfo=timezone.utc)
    now = checked_at + timedelta(hours=24)

    assert is_recheck_due("high", checked_at, now) is True


def test_unknown_volatility_raises_error():
    with pytest.raises(ValueError):
        calculate_next_check("extreme")
