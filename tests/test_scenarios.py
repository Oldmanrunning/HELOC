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


def test_custom_scenario_stress_inputs_change_outputs():
    df = build_scenario_comparison(
        borrowed=75000,
        apr=0.08,
        period_years=15,
        home_value=500000,
        existing_loan=250000,
        alternative_apr=0.1,
        stress_apr_shift=0.03,
        home_value_drop_pct=0.20,
        credit_card_apr=0.22,
    )

    stressed_rate = df[df["Scenario"] == "HELOC with APR +2%"].iloc[0]
    home_decline = df[df["Scenario"] == "HELOC with Home Value -10%"].iloc[0]

    assert stressed_rate["APR"] == 0.11
    assert stressed_rate["Total Interest"] > df.iloc[0]["Total Interest"]
    assert home_decline["Home Value"] == 400000
    assert home_decline["CLTV"] > df.iloc[0]["CLTV"]
