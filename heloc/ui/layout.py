from datetime import datetime

import pandas as pd
import streamlit as st

from heloc.calculations.amortization import amortize_schedule
from heloc.calculations.risk import calculate_risk_score, loan_to_value
from heloc.calculations.scenarios import build_scenario_comparison, choose_best_option, estimated_loan_amount
from heloc.reports.pdf_report import build_pdf_report
from heloc.visualizations.charts import render_balance_chart


def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"


def render_results(values: dict) -> None:
    apr = values["APR_pct"] / 100.0
    apr_alt = values["APR_alt_pct"] / 100.0
    estimated_loan = estimated_loan_amount(values["Borrowed"], values["Existing_loan"])
    ltv = loan_to_value(estimated_loan, values["Home_value"])

    start = pd.Timestamp(datetime.today().date())
    m, _tot, intr, sched = amortize_schedule(values["Borrowed"], apr, values["Period_years"], start_date=start)
    m_alt, _tot_alt, intr_alt, _sched_alt = amortize_schedule(values["Borrowed"], apr_alt, values["Period_years"], start_date=start)

    risk = calculate_risk_score(
        borrowed=values["Borrowed"],
        existing_loan=values["Existing_loan"],
        home_value=values["Home_value"],
        apr=apr,
        period_years=values["Period_years"],
        monthly_payment=m,
        application_fee=values["Application_fee"],
        annual_fee=values["Annual_fee"],
        appraisal_fee=values["Appraisal_fee"],
        origination_fee=values["Origination_fee"],
        closing_costs=values["Closing_costs"],
        monthly_income=values["Monthly_income"] or None,
        monthly_debt=values["Monthly_debt"] or None,
    )

    st.subheader("Quick summary")
    k1, k2, k3 = st.columns(3)
    k1.metric("Monthly Payment", fmt_usd(m))
    k2.metric("Total Interest", fmt_usd(intr))
    k3.metric("Loan-to-Value (LTV)", f"{ltv:.2%}")

    st.markdown("---")
    tabs = st.tabs(["Details", "Amortization", "Alternative APR", "Risk Intelligence", "Scenario Modeling", "Export"])

    with tabs[0]:
        st.header("Details")
        st.markdown(
            f"""
            - **Borrowed:** {fmt_usd(values['Borrowed'])}
            - **APR:** {values['APR_pct']:.2f}%
            - **Payment Period:** {values['Period_years']} years
            - **Estimated Loan Amount:** {fmt_usd(estimated_loan)}
            - **LTV:** {ltv:.2%}
            - **Application Fee:** {fmt_usd(values['Application_fee'])}
            - **Closing Costs:** {fmt_usd(values['Closing_costs'])}
            """
        )

    with tabs[1]:
        st.header("Amortization schedule (first 24 months)")
        if sched.empty:
            st.info("No schedule (zero principal or period).")
        else:
            st.dataframe(sched.head(24).assign(payment=lambda df: df["payment"].map(fmt_usd)))
            render_balance_chart(sched)

    with tabs[2]:
        st.header("Compare to alternative APR")
        st.markdown(
            f"- **Alt APR:** {values['APR_alt_pct']:.2f}%  \n"
            f"- **Monthly (alt):** {fmt_usd(m_alt)}  \n"
            f"- **Total interest (alt):** {fmt_usd(intr_alt)}"
        )
        st.write("Difference in monthly payment:", fmt_usd(m_alt - m))
        st.write("Difference in total interest:", fmt_usd(intr_alt - intr))

    with tabs[3]:
        st.header("Risk Intelligence")
        st.metric("Risk Score", f"{risk['score']:.1f} / 100")
        level_colors = {"Low": "#2e7d32", "Moderate": "#ef6c00", "Elevated": "#d84315", "High": "#b71c1c"}
        st.markdown(
            f"<span style='background:{level_colors.get(risk['level'], '#37474f')};color:white;padding:0.35rem 0.65rem;border-radius:0.5rem;font-weight:600;'>Risk Level: {risk['level']}</span>",
            unsafe_allow_html=True,
        )
        st.subheader("Strengths")
        for item in risk["strengths"]:
            st.markdown(f"- {item}")
        st.subheader("Watch areas")
        for item in risk["watch_areas"]:
            st.markdown(f"- {item}")
        st.subheader("Recommendation")
        st.info(risk["recommendation"])

    with tabs[4]:
        st.header("Scenario Modeling")
        c1, c2, c3 = st.columns(3)
        with c1:
            stress_apr_shift_pct = st.number_input("APR stress delta (%)", min_value=0.0, value=2.0, step=0.1, format="%.2f")
        with c2:
            home_value_drop_pct = st.number_input("Home value decline (%)", min_value=0.0, value=10.0, step=1.0, format="%.1f")
        with c3:
            credit_card_apr_pct = st.number_input("Credit card APR (%)", min_value=0.0, value=24.0, step=0.1, format="%.2f")

        scenario_df = build_scenario_comparison(
            borrowed=values["Borrowed"],
            apr=apr,
            period_years=values["Period_years"],
            home_value=values["Home_value"],
            existing_loan=values["Existing_loan"],
            alternative_apr=apr_alt,
            stress_apr_shift=stress_apr_shift_pct / 100.0,
            home_value_drop_pct=home_value_drop_pct / 100.0,
            credit_card_apr=credit_card_apr_pct / 100.0,
        )

        best_option = choose_best_option(scenario_df)
        st.success(f"Best Option (lowest total repayment): **{best_option}**")

        display_df = scenario_df.copy()
        for col in ["APR", "LTV", "CLTV"]:
            display_df[col] = display_df[col].map(lambda x: f"{x:.2%}")
        for col in [
            "Monthly Payment",
            "Total Interest",
            "Total Repayment",
            "Diff Monthly vs Current",
            "Diff Interest vs Current",
            "Diff Repayment vs Current",
        ]:
            display_df[col] = display_df[col].map(fmt_usd)

        st.dataframe(display_df, use_container_width=True)

        top = scenario_df.sort_values("Total Repayment").iloc[0]
        base = scenario_df[scenario_df["Scenario"] == "Current HELOC"].iloc[0]
        delta = top["Total Repayment"] - base["Total Repayment"]
        direction = "lower" if delta < 0 else "higher"
        st.markdown(
            f"Under the current assumptions, **{top['Scenario']}** has the lowest projected total repayment. "
            f"Compared with the current HELOC, it is **{fmt_usd(abs(delta))} {direction}** over the modeled term."
        )

    with tabs[5]:
        st.header("Export")
        st.write("Download amortization schedule as CSV for further analysis or printing.")
        csv = sched.to_csv(index=False)
        st.download_button("Download schedule (CSV)", data=csv, file_name="amortization_schedule.csv", mime="text/csv")
        report_md = f"""
        HELOC Summary as of {datetime.today().date()}
        - Borrowed: {fmt_usd(values['Borrowed'])}
        - APR: {values['APR_pct']:.2f}%
        - Monthly payment: {fmt_usd(m)}
        - Total interest: {fmt_usd(intr)}
        """
        st.download_button("Download short report (TXT)", data=report_md, file_name="heloc_summary.txt", mime="text/plain")
        scenario_df = build_scenario_comparison(
            borrowed=values["Borrowed"],
            apr=apr,
            period_years=values["Period_years"],
            home_value=values["Home_value"],
            existing_loan=values["Existing_loan"],
            alternative_apr=apr_alt,
            stress_apr_shift=0.02,
            home_value_drop_pct=0.10,
            credit_card_apr=0.24,
        )
        pdf_bytes = build_pdf_report(
            borrower_assumptions={
                "Borrowed": fmt_usd(values["Borrowed"]),
                "Home Value": fmt_usd(values["Home_value"]),
                "Existing Loan": fmt_usd(values["Existing_loan"]),
                "Term": f"{values['Period_years']} years",
                "HELOC APR": f"{values['APR_pct']:.2f}%",
                "Alternative APR": f"{values['APR_alt_pct']:.2f}%",
                "Monthly Income (optional)": fmt_usd(values["Monthly_income"]),
                "Monthly Debt (optional)": fmt_usd(values["Monthly_debt"]),
            },
            loan_summary={
                "Estimated Loan Amount": fmt_usd(estimated_loan),
                "Monthly Payment": fmt_usd(m),
                "Total Interest": fmt_usd(intr),
                "Loan-to-Value (LTV)": f"{ltv:.2%}",
                "Application Fee": fmt_usd(values["Application_fee"]),
                "Annual Fee": fmt_usd(values["Annual_fee"]),
                "Appraisal Fee": fmt_usd(values["Appraisal_fee"]),
                "Origination Fee": fmt_usd(values["Origination_fee"]),
                "Closing Costs": fmt_usd(values["Closing_costs"]),
            },
            risk=risk,
            scenario_df=scenario_df,
            total_interest_comparison={
                "Current HELOC": intr,
                "Alternative APR": intr_alt,
                "Difference (Alt - Current)": intr_alt - intr,
            },
        )
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name=f"heloc_financial_decision_report_{datetime.today().date()}.pdf",
            mime="application/pdf",
        )
