from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RiskResult:
    score: float
    level: str
    strengths: List[str]
    watch_areas: List[str]
    recommendation: str


def loan_to_value(estimated_loan: float, home_value: float) -> float:
    return (estimated_loan / home_value) if home_value else 0.0


def calculate_risk_score(
    *,
    borrowed: float,
    existing_loan: float,
    home_value: float,
    apr: float,
    period_years: int,
    monthly_payment: float,
    application_fee: float,
    annual_fee: float,
    appraisal_fee: float,
    origination_fee: float,
    closing_costs: float,
    monthly_income: Optional[float] = None,
    monthly_debt: Optional[float] = None,
) -> Dict[str, object]:
    score = 100.0
    strengths: List[str] = []
    watch_areas: List[str] = []

    estimated_loan = borrowed + existing_loan
    ltv = loan_to_value(borrowed, home_value)
    cltv = loan_to_value(estimated_loan, home_value)

    if ltv <= 0.50:
        strengths.append("Low primary LTV supports stronger equity positioning.")
    elif ltv <= 0.80:
        score -= 8
    else:
        score -= 18
        watch_areas.append("Primary LTV is elevated, reducing the equity cushion.")

    if cltv <= 0.70:
        strengths.append("Combined LTV is conservative relative to home value.")
    elif cltv <= 0.85:
        score -= 10
        watch_areas.append("Combined LTV is moderate and should be monitored.")
    else:
        score -= 22
        watch_areas.append("Combined LTV is high and increases refinancing/sale risk.")

    if borrowed <= 50000:
        strengths.append("Borrowed amount is relatively contained.")
    elif borrowed <= 150000:
        score -= 6
    else:
        score -= 12
        watch_areas.append("Borrowed amount is sizable and may pressure repayment flexibility.")

    if apr <= 0.08:
        strengths.append("APR is favorable and limits long-run interest drag.")
    elif apr <= 0.12:
        score -= 8
    else:
        score -= 18
        watch_areas.append("APR is high and can materially increase repayment cost.")

    if period_years <= 10:
        strengths.append("Shorter payoff horizon supports faster deleveraging.")
    elif period_years <= 20:
        score -= 6
    else:
        score -= 12
        watch_areas.append("Long repayment period extends exposure to rate and life-event risk.")

    if monthly_income and monthly_income > 0:
        burden = monthly_payment / monthly_income
        dti = ((monthly_debt or 0.0) + monthly_payment) / monthly_income

        if burden <= 0.20:
            strengths.append("Monthly payment burden appears manageable versus income.")
        elif burden <= 0.35:
            score -= 8
            watch_areas.append("Monthly payment burden is moderate; maintain cash-flow discipline.")
        else:
            score -= 18
            watch_areas.append("Monthly payment burden is high relative to income.")

        if dti <= 0.36:
            strengths.append("Estimated debt-to-income profile is within common lending guardrails.")
        elif dti <= 0.43:
            score -= 8
        else:
            score -= 16
            watch_areas.append("Estimated debt-to-income level is elevated.")
    else:
        watch_areas.append("Monthly income/debt not provided; cash-flow affordability could not be fully assessed.")

    fees_total = application_fee + annual_fee + appraisal_fee + origination_fee + closing_costs
    fee_ratio = (fees_total / borrowed) if borrowed > 0 else 0.0
    if fee_ratio <= 0.03:
        strengths.append("Fees and closing costs are efficient relative to borrowing amount.")
    elif fee_ratio <= 0.06:
        score -= 6
    else:
        score -= 12
        watch_areas.append("Fees and closing costs are high as a share of borrowed amount.")

    score = max(0.0, min(100.0, score))

    if score >= 80:
        level = "Low"
        recommendation = "This profile looks healthy. Keep reserves in place and periodically re-evaluate rates and repayment pace."
    elif score >= 60:
        level = "Moderate"
        recommendation = "Risk is manageable with discipline. Focus on reducing principal early and avoiding additional high-cost debt."
    elif score >= 40:
        level = "Elevated"
        recommendation = "Risk is elevated. Consider lowering borrowing, shortening term, or improving monthly cash-flow before proceeding."
    else:
        level = "High"
        recommendation = "Risk is high. Rework core terms (amount, APR, or duration) and stabilize affordability before taking this HELOC."

    return RiskResult(
        score=round(score, 1),
        level=level,
        strengths=strengths,
        watch_areas=watch_areas,
        recommendation=recommendation,
    ).__dict__
