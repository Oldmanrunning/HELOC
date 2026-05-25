from heloc.calculations.risk import loan_to_value


def test_ltv_standard_case():
    assert loan_to_value(250000, 500000) == 0.5


def test_ltv_zero_home_value():
    assert loan_to_value(250000, 0) == 0.0
