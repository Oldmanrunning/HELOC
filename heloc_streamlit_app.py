#!/usr/bin/env python
# coding: utf-8

# In[1]:


# heloctools.py
import pandas as pd
import numpy as np
from functools import lru_cache
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional

def validate_positive(name: str, value: float):
    if value is None:
        raise ValueError(f"{name} is required.")
    try:
        v = float(value)
    except Exception:
        raise ValueError(f"{name} must be numeric.")
    if v <= 0:
        raise ValueError(f"{name} must be > 0.")
    return v

def validate_rate(name: str, value: float):
    v = validate_positive(name, value)
    if v >= 100:
        raise ValueError(f"{name} seems too high — enter a percentage between 0 and 100.")
    return v

def monthly_payment(principal: float, annual_rate_pct: float, term_years: float, payments_per_year: int = 12, interest_only: bool=False) -> float:
    """
    Standard fixed-rate monthly payment. If interest_only True, returns interest-only payment.
    """
    r = annual_rate_pct / 100.0
    p = principal
    n = int(term_years * payments_per_year)
    if interest_only:
        return (p * r) / payments_per_year
    if r == 0:
        return p / n
    i = r / payments_per_year
    payment = (p * i) / (1 - (1 + i)**(-n))
    return payment

@lru_cache(maxsize=256)
def amortization_schedule_cached(principal: float, annual_rate_pct: float, term_years: float,
                                 payments_per_year: int = 12, start_date: Optional[str] = None,
                                 interest_only: bool=False, draw_schedule_json: Optional[str]=None) -> str:
    """
    Returns JSON string of amortization schedule. Using lru_cache for repeated runs with same params.
    draw_schedule_json: JSON string describing draws e.g. [{"month":0,"amount":10000},...]
    """
    df = amortization_schedule(principal, annual_rate_pct, term_years,
                               payments_per_year, start_date, interest_only, draw_schedule_json)
    return df.to_json(date_format='iso', orient='records')

def amortization_schedule(principal: float, annual_rate_pct: float, term_years: float,
                          payments_per_year: int = 12, start_date: Optional[str] = None,
                          interest_only: bool=False, draw_schedule_json: Optional[str]=None) -> pd.DataFrame:
    # Validation
    principal = float(principal)
    annual_rate_pct = float(annual_rate_pct)
    term_years = float(term_years)
    payments_per_year = int(payments_per_year)
    if start_date is None:
        start_date = datetime.today().date()
    else:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()

    draws = []
    if draw_schedule_json:
        try:
            draws = json.loads(draw_schedule_json)
        except Exception:
            # expecting list of dicts with 'month' and 'amount'
            draws = []

    # compute payment
    payment = monthly_payment(principal, annual_rate_pct, term_years, payments_per_year, interest_only)
    # schedule
    n_periods = int(term_years * payments_per_year)
    i = (annual_rate_pct / 100.0) / payments_per_year
    balance = principal
    rows = []
    for period in range(1, n_periods + 1):
        date = start_date + pd.DateOffset(months=period-1)  # requires pandas DateOffset
        draw_amt = 0.0
        # handle draws specified for a given period (month index starting at 0)
        for d in draws:
            if int(d.get("month", -1)) == period - 1:
                draw_amt += float(d.get("amount", 0.0))
        # if draw occurs, add to balance before interest calculation
        balance += draw_amt
        if interest_only:
            interest = balance * i
            principal_payment = 0.0
            if period == n_periods:
                # final balloon: pay principal
                principal_payment = balance
            payment_amt = interest if period < n_periods else interest + principal_payment
        else:
            interest = balance * i
            principal_payment = payment - interest
            payment_amt = payment
            if principal_payment > balance:
                principal_payment = balance
                payment_amt = interest + principal_payment
        balance = max(0.0, balance - principal_payment)
        rows.append({
            "period": period,
            "date": pd.Timestamp(date),
            "payment": round(payment_amt, 2),
            "principal": round(principal_payment, 2),
            "interest": round(interest, 2),
            "draw": round(draw_amt, 2),
            "balance": round(balance, 2)
        })
        if balance <= 0:
            break

    df = pd.DataFrame(rows)
    # reorder a few columns
    df = df[["period", "date", "draw", "payment", "principal", "interest", "balance"]]
    return df

def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    total_paid = df["payment"].sum() + df["draw"].sum()
    total_interest = df["interest"].sum()
    monthly = df.loc[0, "payment"] if not df.empty else 0.0
    remaining_balance = float(df.iloc[-1]["balance"]) if not df.empty else 0.0
    next_payment_due = df.loc[df["balance"]>0, "date"].iloc[0].date() if (not df.empty and (df["balance"]>0).any()) else None
    return {
        "monthly_payment": round(monthly, 2),
        "total_interest": round(total_interest, 2),
        "total_paid": round(total_paid, 2),
        "remaining_balance": round(remaining_balance, 2),
        "next_payment_due": str(next_payment_due)
    }

def scenario_to_json(scenario: Dict[str, Any]) -> str:
    return json.dumps(scenario, default=str)

def scenario_from_json(s: str) -> Dict[str, Any]:
    return json.loads(s)

def presets() -> Dict[str, Dict[str, Any]]:
    return {
        "Short term": {"principal": 50000, "annual_rate_pct": 4.5, "term_years": 5, "interest_only": False},
        "Variable-rate": {"principal": 50000, "annual_rate_pct": 3.5, "term_years": 10, "interest_only": False, "variable": True},
        "Interest-only": {"principal": 50000, "annual_rate_pct": 5.0, "term_years": 10, "interest_only": True}
    }


# In[ ]:




