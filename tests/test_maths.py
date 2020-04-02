import pytest
from datetime import date
from freezegun import freeze_time
from main import compute_days_remaining_in_present_month

class TestMaths:
    """ Tests for various math calculations
    """
    @freeze_time("2020-02-14")
    def test_compute_days_remaining_in_present_month(self):
        assert compute_days_remaining_in_present_month(28) == 14