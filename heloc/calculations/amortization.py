from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd


SCHEDULE_COLUMNS = ["month", "date", "payment", "principal", "interest", "balance"]


def amortize_schedule(
    principal: float,
    apr: float,
    years: int,
    start_date: Optional[pd.Timestamp] = None,
) -> Tuple[float, float, float, pd.DataFrame]:
    """Return (monthly_payment, total_paid, total_interest, schedule_df)."""
    n = int(years * 12)
    if n <= 0 or principal <= 0:
        return 0.0, 0.0, 0.0, pd.DataFrame(columns=SCHEDULE_COLUMNS)

    if apr == 0:
        monthly = principal / n
        total_paid = monthly * n
        total_interest = total_paid - principal
        balance = principal
        rows = []
        for i in range(1, n + 1):
            principal_paid = monthly
            interest_paid = 0.0
            balance -= principal_paid
            date = (start_date + pd.DateOffset(months=i - 1)).date() if start_date is not None else None
            rows.append([i, date, monthly, principal_paid, interest_paid, max(balance, 0.0)])
        df = pd.DataFrame(rows, columns=SCHEDULE_COLUMNS)
        return monthly, total_paid, total_interest, df

    r = apr / 12.0
    factor = (1 + r) ** n
    monthly = principal * (r * factor) / (factor - 1)
    total_paid = monthly * n
    total_interest = total_paid - principal
    balance = principal
    rows = []
    for i in range(1, n + 1):
        interest_paid = balance * r
        principal_paid = monthly - interest_paid
        balance -= principal_paid
        date = (start_date + pd.DateOffset(months=i - 1)).date() if start_date is not None else None
        rows.append([i, date, monthly, principal_paid, interest_paid, max(balance, 0.0)])

    df = pd.DataFrame(rows, columns=SCHEDULE_COLUMNS)
    return monthly, total_paid, total_interest, df
