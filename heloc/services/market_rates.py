"""Market-rate lookup helpers for optional HELOC benchmark context.

The app can enrich HELOC results with a live benchmark when a FRED API key is
configured, but it must remain useful in local/demo environments. All public
helpers therefore return clearly labelled default/sample rates instead of
raising if configuration or network access is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from typing import Any, Callable, Dict, Optional

import requests

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
PRIME_RATE_SERIES_ID = "DPRIME"
PRIME_RATE_LABEL = "U.S. Bank Prime Loan Rate"
DEFAULT_BENCHMARK_RATE = 8.50
DEFAULT_BENCHMARK_DATE = "sample/default"
DEFAULT_SOURCE_LABEL = "Sample/default market rate (not live)"


@dataclass(frozen=True)
class MarketRateContext:
    """Display-ready market-rate context for comparing a user APR to a benchmark."""

    benchmark_rate: float
    benchmark_label: str
    date_retrieved: str
    source_label: str
    is_live: bool
    comparison: str
    interpretation: str


def get_market_rate_context(user_apr_pct: float) -> MarketRateContext:
    """Return live FRED context when available, otherwise a safe sample fallback.

    Args:
        user_apr_pct: The user's HELOC APR as a percentage, e.g. ``8.5``.

    The function intentionally catches configuration, parsing, and request
    failures so Streamlit rendering never crashes because market data is
    unavailable.
    """

    return _build_context(user_apr_pct=user_apr_pct, benchmark=_fetch_fred_prime_rate())


def _fetch_fred_prime_rate(
    *,
    api_key: Optional[str] = None,
    request_get: Callable[..., Any] = requests.get,
) -> Optional[Dict[str, Any]]:
    """Fetch the latest FRED prime-rate observation, or ``None`` on failure."""

    key = api_key if api_key is not None else os.getenv("FRED_API_KEY")
    if not key:
        return None

    try:
        response = request_get(
            FRED_OBSERVATIONS_URL,
            params={
                "series_id": PRIME_RATE_SERIES_ID,
                "api_key": key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            },
            timeout=5,
        )
        response.raise_for_status()
        observations = response.json().get("observations", [])
        if not observations:
            return None

        latest = observations[0]
        value = latest.get("value")
        if value in (None, "."):
            return None

        return {
            "benchmark_rate": float(value),
            "benchmark_label": PRIME_RATE_LABEL,
            "date_retrieved": latest.get("date") or date.today().isoformat(),
            "source_label": "FRED API — U.S. Bank Prime Loan Rate (DPRIME)",
            "is_live": True,
        }
    except (Exception,):
        return None


def _build_context(user_apr_pct: float, benchmark: Optional[Dict[str, Any]]) -> MarketRateContext:
    if benchmark is None:
        benchmark = {
            "benchmark_rate": DEFAULT_BENCHMARK_RATE,
            "benchmark_label": PRIME_RATE_LABEL,
            "date_retrieved": DEFAULT_BENCHMARK_DATE,
            "source_label": DEFAULT_SOURCE_LABEL,
            "is_live": False,
        }

    benchmark_rate = float(benchmark["benchmark_rate"])
    spread = user_apr_pct - benchmark_rate
    comparison = _format_comparison(user_apr_pct, benchmark_rate, spread)
    interpretation = _interpret_spread(spread, bool(benchmark["is_live"]))

    return MarketRateContext(
        benchmark_rate=benchmark_rate,
        benchmark_label=str(benchmark["benchmark_label"]),
        date_retrieved=str(benchmark["date_retrieved"]),
        source_label=str(benchmark["source_label"]),
        is_live=bool(benchmark["is_live"]),
        comparison=comparison,
        interpretation=interpretation,
    )


def _format_comparison(user_apr_pct: float, benchmark_rate: float, spread: float) -> str:
    if abs(spread) < 0.005:
        return f"Your APR of {user_apr_pct:.2f}% is in line with the {benchmark_rate:.2f}% benchmark."

    direction = "above" if spread > 0 else "below"
    return (
        f"Your APR of {user_apr_pct:.2f}% is {abs(spread):.2f} percentage points "
        f"{direction} the {benchmark_rate:.2f}% benchmark."
    )


def _interpret_spread(spread: float, is_live: bool) -> str:
    source_note = "live market benchmark" if is_live else "sample/default benchmark"

    if spread <= -0.50:
        return (
            f"This APR appears favorable versus the {source_note}. Confirm fees, draw-period terms, "
            "and variable-rate adjustment rules before relying on the headline rate."
        )
    if spread < 0.50:
        return (
            f"This APR is close to the {source_note}. Fees, credit-line flexibility, and repayment "
            "terms may matter more than a small rate difference."
        )
    if spread < 2.00:
        return (
            f"This APR is modestly higher than the {source_note}. It may still be reasonable depending "
            "on credit profile, lien position, fees, and lender terms."
        )

    return (
        f"This APR is meaningfully higher than the {source_note}. Consider comparing other lenders or "
        "asking whether credit score, combined loan-to-value, or fees are driving the spread."
    )
