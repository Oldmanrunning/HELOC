import pytest

from heloc.calculations.amortization import amortize_schedule


def test_amortization_zero_apr_has_no_interest():
    monthly, total_paid, total_interest, schedule = amortize_schedule(1200.0, 0.0, 1)
    assert round(monthly, 2) == 100.0
    assert round(total_paid, 2) == 1200.0
    assert round(total_interest, 2) == 0.0
    assert len(schedule) == 12


def test_amortization_handles_zero_principal():
    monthly, total_paid, total_interest, schedule = amortize_schedule(0.0, 0.1, 10)
    assert monthly == 0.0
    assert total_paid == 0.0
    assert total_interest == 0.0
    assert schedule.empty


def test_amortization_schedule_pays_down_to_zero_balance():
    monthly, total_paid, total_interest, schedule = amortize_schedule(12000, 0.06, 1)

    assert monthly > 0
    assert total_paid > 12000
    assert total_interest > 0
    assert len(schedule) == 12
    assert schedule.iloc[-1]["balance"] == pytest.approx(0.0, abs=0.01)
    assert schedule["principal"].sum() == pytest.approx(12000, abs=0.01)


def test_zero_interest_schedule_has_equal_principal_payments():
    monthly, total_paid, total_interest, schedule = amortize_schedule(12000, 0.0, 1)

    assert monthly == pytest.approx(1000.0)
    assert total_paid == pytest.approx(12000.0)
    assert total_interest == pytest.approx(0.0)
    assert schedule["interest"].sum() == pytest.approx(0.0)
    assert schedule["principal"].nunique() == 1
