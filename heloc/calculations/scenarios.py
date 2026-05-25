from __future__ import annotations

import pandas as pd

from heloc.calculations.amortization import amortize_schedule
from heloc.calculations.risk import loan_to_value


def estimated_loan_amount(borrowed: float, existing_loan: float) -> float:
    return borrowed + existing_loan


def _scenario_row(
    name: str,
    borrowed: float,
    apr: float,
    period_years: int,
    home_value: float,
    existing_loan: float,
) -> dict:
    monthly, total_repayment, total_interest, _schedule = amortize_schedule(borrowed, apr, period_years)
    estimated_loan = estimated_loan_amount(borrowed, existing_loan)
    return {
        "Scenario": name,
        "APR": apr,
        "Home Value": home_value,
        "Monthly Payment": monthly,
        "Total Interest": total_interest,
        "Total Repayment": total_repayment,
        "LTV": loan_to_value(borrowed, home_value),
        "CLTV": loan_to_value(estimated_loan, home_value),
    }


def build_scenario_comparison(
    *,
    borrowed: float,
    apr: float,
    period_years: int,
    home_value: float,
    existing_loan: float,
    alternative_apr: float,
    stress_apr_shift: float = 0.02,
    home_value_drop_pct: float = 0.10,
    credit_card_apr: float = 0.24,
) -> pd.DataFrame:
    scenarios = [
        _scenario_row("Current HELOC", borrowed, apr, period_years, home_value, existing_loan),
        _scenario_row("HELOC with APR +2%", borrowed, apr + stress_apr_shift, period_years, home_value, existing_loan),
        _scenario_row("HELOC with Home Value -10%", borrowed, apr, period_years, home_value * (1 - home_value_drop_pct), existing_loan),
        _scenario_row("Alternative Loan APR", borrowed, alternative_apr, period_years, home_value, existing_loan),
        _scenario_row("Credit Card Payoff Comparison", borrowed, credit_card_apr, period_years, home_value, existing_loan),
    ]
    df = pd.DataFrame(scenarios)
    base = df.iloc[0]
    df["Diff Monthly vs Current"] = df["Monthly Payment"] - base["Monthly Payment"]
    df["Diff Interest vs Current"] = df["Total Interest"] - base["Total Interest"]
    df["Diff Repayment vs Current"] = df["Total Repayment"] - base["Total Repayment"]
    return df


def choose_best_option(df: pd.DataFrame) -> str:
    # Primary objective: lower total repayment, tie-breaker on lower monthly payment
    idx = df.sort_values(["Total Repayment", "Monthly Payment"], ascending=True).index[0]
    return str(df.loc[idx, "Scenario"])
