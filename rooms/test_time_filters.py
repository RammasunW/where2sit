"""Unit tests for rooms.templatetags.time_filters (timeline percent math)."""

from datetime import time

import pytest

from rooms.templatetags.time_filters import duration_to_percent, time_to_percent

# Visible day window: 8:00–22:00 → 14 hours = 840 minutes (matches module constants).
_TOTAL_MINUTES = 14 * 60


@pytest.mark.parametrize(
    "t,expected",
    [
        (time(8, 0), 0.0),
        (time(15, 0), 50.0),
        (time(22, 0), 100.0),
        (time(7, 0), 0.0),
        (time(7, 59), 0.0),
    ],
)
def test_time_to_percent(t, expected):
    assert time_to_percent(t) == pytest.approx(expected)


def test_time_to_percent_mid_morning():
    """10:00 is 2 hours after 8:00 → 120/840 of the window."""
    assert time_to_percent(time(10, 0)) == pytest.approx(120 / _TOTAL_MINUTES * 100)


def test_time_to_percent_after_window_not_clamped():
    """After 22:00 the value exceeds 100% (no upper clamp in the filter)."""
    assert time_to_percent(time(23, 0)) == pytest.approx(900 / _TOTAL_MINUTES * 100)


def test_duration_to_percent_two_hours():
    event = {"start": time(10, 0), "end": time(12, 0)}
    assert duration_to_percent(event) == pytest.approx(120 / _TOTAL_MINUTES * 100)


def test_duration_to_percent_zero_length():
    event = {"start": time(14, 30), "end": time(14, 30)}
    assert duration_to_percent(event) == pytest.approx(0.0)


def test_duration_to_percent_one_hour():
    event = {"start": time(9, 0), "end": time(10, 0)}
    assert duration_to_percent(event) == pytest.approx(60 / _TOTAL_MINUTES * 100)
