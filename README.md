# AI-Powered HELOC Financial Decision Intelligence Platform

A polished Streamlit portfolio project that turns Home Equity Line of Credit (HELOC) assumptions into an interactive decision-intelligence dashboard. The app combines amortization math, equity / CLTV diagnostics, market-rate context, scenario modeling, Monte Carlo rate-path forecasting, exportable reports, and optional AI-generated plain-English explanations.

> **Note:** This project is an educational planning tool and portfolio demonstration. It is not financial, legal, tax, credit, or investment advice.

## Project overview

This application helps users evaluate the cost and risk profile of a HELOC by answering practical questions:

- What would my estimated monthly payment and total interest be?
- How does the HELOC compare with another APR or debt product?
- How sensitive is the decision to higher rates or a lower home value?
- Does the borrower profile look low, moderate, elevated, or high risk under transparent rules?
- What could variable-rate uncertainty do to total interest over time?
- Can I export a decision summary for review?

The UI is designed for a GitHub portfolio presentation: professional hero header, executive metrics, tabbed analysis flow, clean input labels, and downloadable CSV / TXT / PDF outputs.

## Screenshots

Add screenshots after running the app locally:

```text
docs/screenshots/01-dashboard-overview.png
docs/screenshots/02-risk-intelligence.png
docs/screenshots/03-scenario-modeling.png
docs/screenshots/04-monte-carlo-forecast.png
```

Suggested GitHub README layout:

| Dashboard Overview | Risk Intelligence |
| --- | --- |
| _Screenshot placeholder_ | _Screenshot placeholder_ |

| Scenario Modeling | Monte Carlo Forecast |
| --- | --- |
| _Screenshot placeholder_ | _Screenshot placeholder_ |

## Features

- **Executive decision snapshot** with monthly payment, total interest, combined loan-to-value, and risk score.
- **Professional input workflow** for draw amount, APR, repayment term, home value, existing liens, fees, alternative APR, and optional affordability data.
- **Amortization engine** that supports fixed-rate payment calculations, zero-interest cases, schedule generation, and balance visualization.
- **Market context** using FRED prime-rate data when `FRED_API_KEY` is configured, with a clearly labeled sample/default fallback for demos.
- **Alternative APR comparison** to compare a HELOC against personal loans, credit cards, or competing lender quotes.
- **Risk Intelligence score** based on LTV / CLTV, borrowed amount, APR, repayment period, fee burden, and optional debt-to-income signals.
- **Scenario Modeling** for APR stress, home-value decline, alternative financing, and credit-card payoff comparison.
- **Monte Carlo Forecast** that simulates APR paths and estimates total-interest uncertainty bands.
- **AI Financial Explanation** powered by the OpenAI API when `OPENAI_API_KEY` is available, with a rule-based fallback when it is not.
- **Export tools** for amortization CSV, short TXT summary, and PDF decision report.
- **Automated tests** for core calculation and service modules.

## Architecture

```text
app.py                         # Streamlit entry point and portfolio-grade shell / hero layout
heloc/
  calculations/
    amortization.py            # Monthly payment and amortization schedule math
    risk.py                    # LTV / CLTV and transparent risk scoring
    scenarios.py               # Scenario comparison table and best-option selection
    monte_carlo.py             # Variable-rate Monte Carlo forecast model
  reports/
    pdf_report.py              # PDF decision report generation
  services/
    ai_advisor.py              # Optional OpenAI explanation with rule-based fallback
    market_rates.py            # Optional FRED benchmark lookup with safe fallback
  ui/
    inputs.py                  # Streamlit input form
    layout.py                  # Results tabs and visual presentation
  visualizations/
    charts.py                  # Chart rendering helpers
tests/                         # Pytest suite for calculations and service fallbacks
```

### Data flow

1. `app.py` renders the hero layout and calls the input form.
2. `heloc/ui/inputs.py` returns a normalized dictionary of borrower and loan assumptions.
3. `heloc/ui/layout.py` orchestrates calculations, tabs, metrics, charts, explanations, and exports.
4. Calculation modules in `heloc/calculations/` remain framework-independent and unit-testable.
5. Service modules enrich the app when API keys are present but fail safely for local portfolio demos.

## How to run locally

### 1. Clone and enter the repository

```bash
git clone <your-repo-url>
cd HELOC
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch Streamlit

```bash
streamlit run app.py
```

Then open the local Streamlit URL displayed in your terminal, usually `http://localhost:8501`.

## Environment variables

All environment variables are optional. Without them, the app still runs with safe demo fallbacks.

| Variable | Required? | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | No | Enables AI-generated educational explanations in the AI Financial Explanation tab. If omitted, a deterministic rule-based explanation is shown. |
| `FRED_API_KEY` | No | Enables live FRED U.S. Bank Prime Loan Rate lookup for market context. If omitted or unavailable, a sample/default benchmark is clearly labeled. |

You can set variables in your shell:

```bash
export OPENAI_API_KEY="your_openai_key"
export FRED_API_KEY="your_fred_key"
```

Or create a local `.env` file for your own workflow. Do not commit secrets.

## Testing instructions

Run the full test suite:

```bash
pytest -q
```

Recommended pre-portfolio checks:

```bash
python -m compileall app.py heloc
pytest -q
streamlit run app.py
```

The tests cover:

- amortization payment math, payoff schedule shape, and zero-interest behavior
- LTV and risk score classification
- scenario comparison and best-option selection
- Monte Carlo forecast summaries and deterministic zero-volatility behavior
- market-rate fallback and FRED response parsing

## Portfolio / resume summary

**AI-Powered HELOC Financial Decision Intelligence Platform** — Built a Streamlit financial analytics dashboard that models HELOC payment schedules, combined loan-to-value exposure, fee burden, alternative financing scenarios, stochastic interest-rate risk, and exportable borrower decision reports. Designed modular, testable Python calculation services with optional FRED and OpenAI integrations that gracefully degrade for local demos.

Suggested resume bullets:

- Developed a portfolio-ready Python / Streamlit HELOC decision platform with amortization, risk scoring, scenario analysis, Monte Carlo forecasting, and PDF exports.
- Engineered modular calculation services with pytest coverage for core financial logic and safe API fallbacks for market-rate and AI integrations.
- Created a professional dashboard UX with executive metrics, tabbed workflows, transparent modeling assumptions, and borrower-friendly explanations.

## Disclaimer

This software is provided for educational and demonstration purposes only. It does not provide financial, legal, tax, credit, or investment advice and does not replace consultation with qualified professionals. HELOC terms, rates, fees, underwriting rules, tax treatment, and borrower outcomes vary by lender, jurisdiction, credit profile, property value, market conditions, and individual circumstances. Always verify assumptions and consult licensed professionals before making financial decisions.

## License

See [LICENSE](LICENSE).
