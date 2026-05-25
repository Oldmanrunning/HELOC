# HELOC Analysis (Streamlit App)

## Project architecture

```text
app.py
heloc/
  calculations/
    amortization.py
    risk.py
    scenarios.py
    monte_carlo.py
  visualizations/
    charts.py
  reports/
    pdf_report.py
  services/
    market_rates.py
    ai_advisor.py
  ui/
    inputs.py
    layout.py
tests/
  test_amortization.py
  test_risk.py
```

### Module responsibilities
- `app.py`: Streamlit entrypoint and top-level page layout.
- `heloc/ui/`: input form and results rendering.
- `heloc/calculations/`: amortization math, LTV, and scenario helpers.
- `heloc/visualizations/`: chart rendering utilities.
- `heloc/reports/`: reporting extension points (PDF generation placeholder).
- `heloc/services/`: service integration extension points (market rates / AI advisor placeholders).
- `tests/`: unit tests for calculation logic.

## Quick start

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

## Features

- HELOC payment and amortization analysis.
- Alternative APR comparison.
- Scenario Modeling tab with editable assumptions and side-by-side option analysis.
- Risk Intelligence scoring (0-100) with strengths, watch areas, and recommendation.
- Optional affordability inputs: monthly income and monthly debt obligations.
