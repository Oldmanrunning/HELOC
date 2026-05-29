from __future__ import annotations

from datetime import date
from typing import Dict

import pandas as pd
from fpdf import FPDF


def _fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2%}"


class HELOCPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "HELOC Financial Decision Report", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, f"Generated: {date.today().isoformat()}", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_title(self, title: str) -> None:
        self.set_x(self.l_margin)
        self.set_fill_color(245, 247, 250)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", fill=True)

    def bullet_list(self, items: list[str]) -> None:
        self.set_font("Helvetica", "", 10)
        for item in items:
            self.multi_cell(0, 6, f"- {item}", new_x="LMARGIN", new_y="NEXT")


def build_pdf_report(
    *,
    borrower_assumptions: Dict[str, str],
    loan_summary: Dict[str, str],
    risk: Dict[str, object],
    scenario_df: pd.DataFrame,
    total_interest_comparison: Dict[str, float],
) -> bytes:
    pdf = HELOCPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.section_title("Borrower assumptions")
    pdf.set_font("Helvetica", "", 10)
    for label, value in borrower_assumptions.items():
        pdf.multi_cell(0, 6, f"{label}: {value}", new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Loan summary")
    pdf.set_font("Helvetica", "", 10)
    for label, value in loan_summary.items():
        pdf.multi_cell(0, 6, f"{label}: {value}", new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Risk score and risk level")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, f"Risk Score: {risk['score']:.1f} / 100", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 6, f"Risk Level: {risk['level']}", new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Strengths")
    pdf.bullet_list(risk["strengths"] or ["No notable strengths identified under current assumptions."])

    pdf.section_title("Watch areas")
    pdf.bullet_list(risk["watch_areas"] or ["No material watch areas identified under current assumptions."])

    pdf.section_title("Recommendation")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, str(risk["recommendation"]), new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Scenario comparison")
    columns = ["Scenario", "APR", "Monthly Payment", "Total Interest", "Total Repayment"]
    table_data = scenario_df[columns].copy()
    table_data["APR"] = table_data["APR"].map(_fmt_pct)
    table_data["Monthly Payment"] = table_data["Monthly Payment"].map(_fmt_usd)
    table_data["Total Interest"] = table_data["Total Interest"].map(_fmt_usd)
    table_data["Total Repayment"] = table_data["Total Repayment"].map(_fmt_usd)

    widths = [48, 20, 38, 38, 38]
    pdf.set_font("Helvetica", "B", 9)
    for idx, col in enumerate(columns):
        pdf.cell(widths[idx], 8, col, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for _, row in table_data.iterrows():
        pdf.cell(widths[0], 7, str(row["Scenario"])[:30], border=1)
        pdf.cell(widths[1], 7, row["APR"], border=1)
        pdf.cell(widths[2], 7, row["Monthly Payment"], border=1)
        pdf.cell(widths[3], 7, row["Total Interest"], border=1)
        pdf.cell(widths[4], 7, row["Total Repayment"], border=1)
        pdf.ln()

    pdf.section_title("Total interest comparison")
    pdf.set_font("Helvetica", "", 10)
    for label, value in total_interest_comparison.items():
        pdf.multi_cell(0, 6, f"{label}: {_fmt_usd(value)}", new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("Disclaimer")
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "This report is an educational planning tool and is not financial, legal, tax, or investment advice. "
        "Consult licensed professionals before making financial decisions.",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    raw_output = pdf.output()
    if isinstance(raw_output, str):
        return raw_output.encode("latin-1")
    return bytes(raw_output)
