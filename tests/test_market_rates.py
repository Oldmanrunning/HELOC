from heloc.services.market_rates import (
    DEFAULT_BENCHMARK_RATE,
    DEFAULT_SOURCE_LABEL,
    _fetch_fred_prime_rate,
    get_market_rate_context,
)


class FailingResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"observations": [{"date": "2026-01-01", "value": "."}]}


class SuccessfulResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"observations": [{"date": "2026-01-02", "value": "7.25"}]}


def test_market_rate_context_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    context = get_market_rate_context(user_apr_pct=9.0)

    assert context.benchmark_rate == DEFAULT_BENCHMARK_RATE
    assert context.source_label == DEFAULT_SOURCE_LABEL
    assert context.is_live is False
    assert "sample/default benchmark" in context.interpretation
    assert "0.50 percentage points above" in context.comparison


def test_fred_fetch_returns_none_when_request_fails():
    def request_get(*args, **kwargs):
        raise RuntimeError("network unavailable")

    assert _fetch_fred_prime_rate(api_key="test-key", request_get=request_get) is None


def test_fred_fetch_returns_none_for_missing_observation_value():
    def request_get(*args, **kwargs):
        return FailingResponse()

    assert _fetch_fred_prime_rate(api_key="test-key", request_get=request_get) is None


def test_fred_fetch_parses_latest_observation():
    def request_get(url, params, timeout):
        assert params["series_id"] == "DPRIME"
        assert timeout == 5
        return SuccessfulResponse()

    result = _fetch_fred_prime_rate(api_key="test-key", request_get=request_get)

    assert result == {
        "benchmark_rate": 7.25,
        "benchmark_label": "U.S. Bank Prime Loan Rate",
        "date_retrieved": "2026-01-02",
        "source_label": "FRED API — U.S. Bank Prime Loan Rate (DPRIME)",
        "is_live": True,
    }
