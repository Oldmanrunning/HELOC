from datetime import datetime

import pandas as pd
import streamlit as st

from heloc.calculations.amortization import amortize_schedule
from heloc.calculations.risk import loan_to_value
from heloc.calculations.scenarios import estimated_loan_amount
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

    st.subheader("Quick summary")
    k1, k2, k3 = st.columns(3)
    k1.metric("Monthly Payment", fmt_usd(m))
    k2.metric("Total Interest", fmt_usd(intr))
    k3.metric("Loan-to-Value (LTV)", f"{ltv:.2%}")

    st.markdown("---")
    tabs = st.tabs(["Details", "Amortization", "Alternative APR", "Export"])

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
        with st.expander("Show all fees and values"):
            st.write(
                {
                    "Application_fee": values["Application_fee"],
                    "Annual_fee": values["Annual_fee"],
                    "Appraisal_fee": values["Appraisal_fee"],
                    "Origination_fee": values["Origination_fee"],
                    "Closing_costs": values["Closing_costs"],
                    "Home_value": values["Home_value"],
                    "Existing_loan": values["Existing_loan"],
                }
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
