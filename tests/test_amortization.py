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
