from heloc.calculations.risk import calculate_risk_score, loan_to_value


def test_ltv_standard_case():
    assert loan_to_value(250000, 500000) == 0.5


def test_ltv_zero_home_value():
    assert loan_to_value(250000, 0) == 0.0


def test_risk_score_low_risk_scenario():
    result = calculate_risk_score(
        borrowed=30000,
        existing_loan=120000,
        home_value=500000,
        apr=0.065,
        period_years=10,
        monthly_payment=340,
        application_fee=250,
        annual_fee=75,
        appraisal_fee=0,
        origination_fee=0,
        closing_costs=500,
        monthly_income=9000,
        monthly_debt=1200,
    )
    assert result["score"] >= 80
    assert result["level"] == "Low"


def test_risk_score_high_risk_scenario():
    result = calculate_risk_score(
        borrowed=180000,
        existing_loan=260000,
        home_value=450000,
        apr=0.19,
        period_years=30,
        monthly_payment=2900,
        application_fee=3000,
        annual_fee=600,
        appraisal_fee=1200,
        origination_fee=5000,
        closing_costs=4500,
        monthly_income=5000,
        monthly_debt=1900,
    )
    assert result["score"] < 40
    assert result["level"] == "High"
    assert len(result["watch_areas"]) > 0
