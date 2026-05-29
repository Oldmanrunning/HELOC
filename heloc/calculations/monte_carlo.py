"""Monte Carlo tools for educational HELOC interest-rate forecasting.

The simulation uses an additive monthly random walk for APRs. The annual APR
volatility input is interpreted as decimal APR volatility: ``0.02`` means an
annualized two-percentage-point volatility. Each month, the payment is
re-amortized over the remaining term at that month's simulated APR, which keeps
the projection transparent while approximating variable-rate payment resets.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

MIN_SIMULATIONS = 1_000
MONTHS_PER_YEAR = 12
MAX_APR = 0.50


def simulate_heloc_interest_rate_paths(
    *,
    starting_apr: float,
    annual_apr_volatility: float,
    years: int,
    principal: float,
    number_of_simulations: int = MIN_SIMULATIONS,
    random_seed: Optional[int] = None,
) -> Dict[str, object]:
    """Simulate HELOC total-interest outcomes under uncertain future APRs.

    Args:
        starting_apr: Starting APR as a decimal, e.g. ``0.085`` for 8.5%.
        annual_apr_volatility: Annualized APR volatility as a decimal, e.g.
            ``0.02`` for two percentage points.
        years: Repayment horizon in years.
        principal: Starting loan balance.
        number_of_simulations: Requested number of paths. The function always
            runs at least ``MIN_SIMULATIONS`` paths.
        random_seed: Optional seed for deterministic tests or reproducible demos.

    Returns:
        A dictionary containing percentile summary values, the probability that
        simulated interest exceeds the fixed-rate baseline by 10%, and a
        simulation-level DataFrame.
    """

    simulation_count = max(int(number_of_simulations), MIN_SIMULATIONS)
    months = max(int(years * MONTHS_PER_YEAR), 0)
    starting_apr = max(float(starting_apr), 0.0)
    annual_apr_volatility = max(float(annual_apr_volatility), 0.0)
    principal = max(float(principal), 0.0)

    baseline_total_interest = _fixed_rate_total_interest(
        principal=principal,
        apr=starting_apr,
        months=months,
    )

    if months == 0 or principal == 0:
        simulation_df = _empty_simulation_frame(simulation_count)
        return _summary_from_frame(simulation_df, baseline_total_interest)

    rng = np.random.default_rng(random_seed)
    monthly_volatility = annual_apr_volatility / np.sqrt(MONTHS_PER_YEAR)
    rate_shocks = rng.normal(loc=0.0, scale=monthly_volatility, size=(simulation_count, months))
    rate_shocks[:, 0] = 0.0
    apr_paths = np.clip(starting_apr + np.cumsum(rate_shocks, axis=1), 0.0, MAX_APR)

    balances = np.full(simulation_count, principal, dtype=float)
    total_interest = np.zeros(simulation_count, dtype=float)

    for month_index in range(months):
        remaining_months = months - month_index
        monthly_rates = apr_paths[:, month_index] / MONTHS_PER_YEAR
        payments = _remaining_term_payments(balances, monthly_rates, remaining_months)
        interest = balances * monthly_rates
        principal_paid = np.minimum(np.maximum(payments - interest, 0.0), balances)
        balances = np.maximum(balances - principal_paid, 0.0)
        total_interest += interest

    simulation_df = pd.DataFrame(
        {
            "simulation": np.arange(1, simulation_count + 1),
            "total_interest": total_interest,
            "average_apr": apr_paths.mean(axis=1),
            "ending_apr": apr_paths[:, -1],
            "max_apr": apr_paths.max(axis=1),
            "ending_balance": balances,
        }
    )
    simulation_df["exceeds_baseline_by_10_pct"] = (
        simulation_df["total_interest"] > baseline_total_interest * 1.10
    )

    return _summary_from_frame(simulation_df, baseline_total_interest)


def build_monte_carlo_interpretation(
    *,
    median_total_interest: float,
    p10_total_interest: float,
    p90_total_interest: float,
    baseline_total_interest: float,
    probability_exceeds_baseline_by_10: float,
) -> str:
    """Create a plain-English explanation for simulated HELOC interest outcomes."""

    if baseline_total_interest <= 0:
        return (
            "The model projects no interest under the current principal or term assumptions. "
            "Increase the principal, APR, or term to explore rate uncertainty."
        )

    median_delta = median_total_interest - baseline_total_interest
    direction = "above" if median_delta > 0 else "below"
    risk_label = _probability_label(probability_exceeds_baseline_by_10)

    return (
        "This educational simulation treats APR changes as a random walk and re-amortizes the "
        "payment each month. The middle simulated outcome is "
        f"{abs(median_delta) / baseline_total_interest:.1%} {direction} the fixed-rate baseline. "
        f"The central 80% of outcomes ranges from ${p10_total_interest:,.0f} to "
        f"${p90_total_interest:,.0f} in total interest. The chance of interest ending more than "
        f"10% above the baseline is {probability_exceeds_baseline_by_10:.1%}, which is {risk_label}."
    )


def _fixed_rate_total_interest(*, principal: float, apr: float, months: int) -> float:
    if principal <= 0 or months <= 0:
        return 0.0

    monthly_rate = apr / MONTHS_PER_YEAR
    if monthly_rate == 0:
        return 0.0

    factor = (1 + monthly_rate) ** months
    monthly_payment = principal * (monthly_rate * factor) / (factor - 1)
    return monthly_payment * months - principal


def _remaining_term_payments(balances: np.ndarray, monthly_rates: np.ndarray, remaining_months: int) -> np.ndarray:
    if remaining_months <= 0:
        return balances

    payments = np.zeros_like(balances)
    zero_rate_mask = monthly_rates <= 0
    payments[zero_rate_mask] = balances[zero_rate_mask] / remaining_months

    rate_mask = ~zero_rate_mask
    rates = monthly_rates[rate_mask]
    factors = (1 + rates) ** remaining_months
    payments[rate_mask] = balances[rate_mask] * (rates * factors) / (factors - 1)
    return payments


def _empty_simulation_frame(simulation_count: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "simulation": np.arange(1, simulation_count + 1),
            "total_interest": np.zeros(simulation_count),
            "average_apr": np.zeros(simulation_count),
            "ending_apr": np.zeros(simulation_count),
            "max_apr": np.zeros(simulation_count),
            "ending_balance": np.zeros(simulation_count),
            "exceeds_baseline_by_10_pct": np.zeros(simulation_count, dtype=bool),
        }
    )


def _summary_from_frame(simulation_df: pd.DataFrame, baseline_total_interest: float) -> Dict[str, object]:
    total_interest = simulation_df["total_interest"]
    return {
        "median_total_interest": float(total_interest.median()),
        "p10_total_interest": float(total_interest.quantile(0.10)),
        "p90_total_interest": float(total_interest.quantile(0.90)),
        "baseline_total_interest": float(baseline_total_interest),
        "probability_exceeds_baseline_by_10": float(simulation_df["exceeds_baseline_by_10_pct"].mean()),
        "simulation_df": simulation_df,
    }


def _probability_label(probability: float) -> str:
    if probability < 0.20:
        return "relatively low under these assumptions"
    if probability < 0.50:
        return "moderate under these assumptions"
    return "elevated under these assumptions"
