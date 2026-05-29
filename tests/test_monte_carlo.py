import pytest

from heloc.calculations.monte_carlo import (
    MIN_SIMULATIONS,
    build_monte_carlo_interpretation,
    simulate_heloc_interest_rate_paths,
)


def test_monte_carlo_enforces_minimum_simulations_and_returns_required_summary():
    result = simulate_heloc_interest_rate_paths(
        starting_apr=0.085,
        annual_apr_volatility=0.02,
        years=10,
        principal=50_000,
        number_of_simulations=25,
        random_seed=7,
    )

    assert set(result) == {
        "median_total_interest",
        "p10_total_interest",
        "p90_total_interest",
        "baseline_total_interest",
        "probability_exceeds_baseline_by_10",
        "simulation_df",
    }
    assert len(result["simulation_df"]) == MIN_SIMULATIONS
    assert result["p10_total_interest"] <= result["median_total_interest"] <= result["p90_total_interest"]
    assert 0.0 <= result["probability_exceeds_baseline_by_10"] <= 1.0


def test_zero_volatility_matches_fixed_rate_baseline():
    result = simulate_heloc_interest_rate_paths(
        starting_apr=0.08,
        annual_apr_volatility=0.0,
        years=5,
        principal=25_000,
        number_of_simulations=1_000,
        random_seed=11,
    )

    assert result["median_total_interest"] == pytest.approx(result["baseline_total_interest"], rel=1e-9)
    assert result["p10_total_interest"] == pytest.approx(result["baseline_total_interest"], rel=1e-9)
    assert result["p90_total_interest"] == pytest.approx(result["baseline_total_interest"], rel=1e-9)
    assert result["probability_exceeds_baseline_by_10"] == 0.0


def test_empty_principal_returns_zero_interest_frame():
    result = simulate_heloc_interest_rate_paths(
        starting_apr=0.08,
        annual_apr_volatility=0.03,
        years=10,
        principal=0,
        number_of_simulations=1_000,
        random_seed=5,
    )

    assert result["median_total_interest"] == 0.0
    assert result["baseline_total_interest"] == 0.0
    assert result["simulation_df"]["total_interest"].sum() == 0.0


def test_interpretation_describes_model_and_probability():
    interpretation = build_monte_carlo_interpretation(
        median_total_interest=12_000,
        p10_total_interest=9_000,
        p90_total_interest=18_000,
        baseline_total_interest=10_000,
        probability_exceeds_baseline_by_10=0.42,
    )

    assert "random walk" in interpretation
    assert "10% above the baseline" in interpretation
    assert "moderate" in interpretation
