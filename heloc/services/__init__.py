"""External service integrations and safe fallbacks."""

from heloc.services.ai_advisor import build_explanation_summary, get_ai_financial_explanation
from heloc.services.market_rates import get_market_rate_context

__all__ = ["build_explanation_summary", "get_ai_financial_explanation", "get_market_rate_context"]
