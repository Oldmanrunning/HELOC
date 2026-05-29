import pandas as pd

from heloc.reports.pdf_report import build_pdf_report


def test_build_pdf_report_returns_pdf_bytes():
    scenario_df = pd.DataFrame(
        {
            "Scenario": ["Current HELOC", "Alternative Loan APR"],
            "APR": [0.085, 0.07],
            "Monthly Payment": [620.0, 580.0],
            "Total Interest": [24500.0, 19600.0],
            "Total Repayment": [74500.0, 69600.0],
        }
    )

    pdf_bytes = build_pdf_report(
        borrower_assumptions={"Borrowed": "$50,000.00", "Term": "10 years"},
        loan_summary={"Monthly Payment": "$620.00", "Combined LTV": "62.50%"},
        risk={
            "score": 84.0,
            "level": "Low",
            "strengths": ["Conservative combined LTV."],
            "watch_areas": [],
            "recommendation": "Keep reserves in place.",
        },
        scenario_df=scenario_df,
        total_interest_comparison={"Current HELOC": 24500.0, "Alternative APR": 19600.0},
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
