from heloc.calculations.scenarios import build_scenario_comparison, choose_best_option


def test_scenario_comparison_includes_required_rows():
    df = build_scenario_comparison(
        borrowed=50000,
        apr=0.085,
        period_years=10,
        home_value=400000,
        existing_loan=200000,
        alternative_apr=0.07,
    )
    assert len(df) == 5
    assert set(df["Scenario"].tolist()) == {
        "Current HELOC",
        "HELOC with APR +2%",
        "HELOC with Home Value -10%",
        "Alternative Loan APR",
        "Credit Card Payoff Comparison",
    }


def test_best_option_prefers_lowest_repayment():
    df = build_scenario_comparison(
        borrowed=30000,
        apr=0.09,
        period_years=10,
        home_value=500000,
        existing_loan=100000,
        alternative_apr=0.06,
    )
    assert choose_best_option(df) == "Alternative Loan APR"
