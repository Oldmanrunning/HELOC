"""Framework-independent financial calculation utilities."""

from heloc.calculations.amortization import amortize_schedule
from heloc.calculations.risk import calculate_risk_score, loan_to_value
from heloc.calculations.scenarios import build_scenario_comparison, choose_best_option, estimated_loan_amount

__all__ = [
    "amortize_schedule",
    "calculate_risk_score",
    "loan_to_value",
    "build_scenario_comparison",
    "choose_best_option",
    "estimated_loan_amount",
]
