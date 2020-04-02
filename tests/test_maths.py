import pytest
from datetime import date
from freezegun import freeze_time
from main import compute_days_remaining_in_present_month, get_days_in_month

class TestComputeDaysRemainingInPresentMonth:
    """ Tests for compute_days_remaining_in_present_month
    """
    @freeze_time("2020-02-14")
    def test_before_end_of_month_returns_days_difference(self):
        assert compute_days_remaining_in_present_month(28) == 14

class TestGetDaysInMonth:
    """ Tests for get_days_in_month
    """
    def test_returns_correct_months_per_month(self):
         assert get_days_in_month(1, 2020) == 31
         assert get_days_in_month(2, 2020) == 29
         assert get_days_in_month(4, 2020) == 30