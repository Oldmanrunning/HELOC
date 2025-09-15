# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

st.set_page_config(page_title="HELOC Calculator", layout="wide")

# --- Utilities --------------------------------------------------------------
def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"

def amortize_schedule(principal: float, apr: float, years: int, start_date=None):
    """Return (monthly_payment, total_paid, total_interest, schedule_df)."""
    n = int(years * 12)
    if n <= 0 or principal <= 0:
        df = pd.DataFrame(columns=["month","date","payment","principal","interest","balance"])
        return 0.0, 0.0, 0.0, df
    if apr == 0:
        monthly = principal / n
        total_paid = monthly * n
        total_interest = total_paid - principal
        balance = principal
        rows = []
        for i in range(1, n+1):
            principal_paid = monthly
            interest_paid = 0.0
            balance -= principal_paid
            date = (start_date + pd.DateOffset(months=i-1)).date() if start_date is not None else None
            rows.append([i, date, monthly, principal_paid, interest_paid, max(balance,0.0)])
        df = pd.DataFrame(rows, columns=["month","date","payment","principal","interest","balance"])
        return monthly, total_paid, total_interest, df
    r = apr / 12.0
    factor = (1 + r) ** n
    monthly = principal * (r * factor) / (factor - 1)
    total_paid = monthly * n
    total_interest = total_paid - principal
    balance = principal
    rows = []
    for i in range(1, n+1):
        interest_paid = balance * r
        principal_paid = monthly - interest_paid
        balance -= principal_paid
        date = (start_date + pd.DateOffset(months=i-1)).date() if start_date is not None else None
        rows.append([i, date, monthly, principal_paid, interest_paid, max(balance,0.0)])
    df = pd.DataFrame(rows, columns=["month","date","payment","principal","interest","balance"])
    return monthly, total_paid, total_interest, df

# --- Layout & input form ----------------------------------------------------
st.title("HELOC Calculator")
st.caption("Responsive layout — works on desktop, tablet, and phones")

# Two-column layout: left for inputs, right for results.
left_col, right_col = st.columns([1, 2])

with left_col:
    with st.form("inputs_form"):
        st.header("Inputs")
        # High-level inputs: use slider + number input
        Borrowed = st.slider("Borrowed (USD)", min_value=0.0, max_value=200000.0, value=50000.0, step=100.0, format="%.0f")
        Borrowed_exact = st.number_input("Borrowed (exact)", value=Borrowed, step=100.0, format="%.2f")
        if Borrowed_exact != Borrowed:
            Borrowed = Borrowed_exact

        APR_pct = st.number_input("HELOC APR (%)", min_value=0.0, value=8.5, step=0.01, format="%.2f")
        Period_years = st.slider("Payment Period (years)", 1, 30, 10)
        
        st.write("**Fees & other values**")
        colA, colB = st.columns(2)
        with colA:
            Application_fee = st.number_input("Application Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            Appraisal_fee = st.number_input("Appraisal Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            Origination_fee = st.number_input("Origination Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        with colB:
            Annual_fee = st.number_input("Annual Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            Closing_costs = st.number_input("Closing Costs (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")

        Home_value = st.number_input("Home Value (USD)", min_value=0.0, value=400000.0, step=1000.0, format="%.2f")
        Existing_loan = st.number_input("Existing Loan (USD)", min_value=0.0, value=200000.0, step=1000.0, format="%.2f")
        
        APR_alt_pct = st.number_input("Alternative APR (%)", min_value=0.0, value=28.0, step=0.1, format="%.2f")
        calc_button = st.form_submit_button("Calculate")
        # end form

# If the user hasn't clicked 'Calculate' yet, still show initial results (optional)
# We'll compute whenever the form is submitted, or show default on first load:
if not calc_button:
    # compute once for default values so page isn't blank
    calc_button = True

if calc_button:
    APR = APR_pct / 100.0
    APR_alt = APR_alt_pct / 100.0
    Estimated_loan = Borrowed + Existing_loan
    LTV = (Estimated_loan / Home_value) if Home_value else 0.0

    # amortization schedules (use pandas date index starting today)
    start = pd.Timestamp(datetime.today().date())
    m, tot, intr, sched = amortize_schedule(Borrowed, APR, Period_years, start_date=start)
    m_alt, tot_alt, intr_alt, sched_alt = amortize_schedule(Borrowed, APR_alt, Period_years, start_date=start)

    # --- Right column: summary, metrics, tabs ---------------------------------
    with right_col:
        # Top quick-metrics row (mobile-friendly stacked metrics)
        st.subheader("Quick summary")
        k1, k2, k3 = st.columns(3)
        k1.metric("Monthly Payment", fmt_usd(m))
        k2.metric("Total Interest", fmt_usd(intr))
        k3.metric("Loan-to-Value (LTV)", f"{LTV:.2%}")

        st.markdown("---")
        tabs = st.tabs(["Details", "Amortization", "Alternative APR", "Export"])
        
        # Details tab: formatted summary (compact)
        with tabs[0]:
            st.header("Details")
            st.markdown(
                f"""
                - **Borrowed:** {fmt_usd(Borrowed)}  
                - **APR:** {APR_pct:.2f}%  
                - **Payment Period:** {Period_years} years  
                - **Estimated Loan Amount:** {fmt_usd(Estimated_loan)}  
                - **LTV:** {LTV:.2%}  
                - **Application Fee:** {fmt_usd(Application_fee)}  
                - **Closing Costs:** {fmt_usd(Closing_costs)}  
                """
            )
            with st.expander("Show all fees and values"):
                st.write({
                    "Application_fee": Application_fee,
                    "Annual_fee": Annual_fee,
                    "Appraisal_fee": Appraisal_fee,
                    "Origination_fee": Origination_fee,
                    "Closing_costs": Closing_costs,
                    "Home_value": Home_value,
                    "Existing_loan": Existing_loan,
                })

        # Amortization tab: show table and small chart
        with tabs[1]:
            st.header("Amortization schedule (first 24 months)")
            if sched.empty:
                st.info("No schedule (zero principal or period).")
            else:
                st.dataframe(sched.head(24).assign(payment=lambda df: df['payment'].map(fmt_usd)))
                # small plot (matplotlib is allowed, but keep simple)
                st.line_chart(sched.set_index("month")["balance"])

        # Alternative APR comparison
        with tabs[2]:
            st.header("Compare to alternative APR")
            st.markdown(
                f"- **Alt APR:** {APR_alt_pct:.2f}%  \n"
                f"- **Monthly (alt):** {fmt_usd(m_alt)}  \n"
                f"- **Total interest (alt):** {fmt_usd(intr_alt)}"
            )
            st.write("Difference in monthly payment:", fmt_usd(m_alt - m))
            st.write("Difference in total interest:", fmt_usd(intr_alt - intr))

        # Export tab: download amortization CSV
        with tabs[3]:
            st.header("Export")
            st.write("Download amortization schedule as CSV for further analysis or printing.")
            csv = sched.to_csv(index=False)
            st.download_button("Download schedule (CSV)", data=csv, file_name="amortization_schedule.csv", mime="text/csv")
            # Optionally offer a brief report
            report_md = f"""
            HELOC Summary as of {datetime.today().date()}
            - Borrowed: {fmt_usd(Borrowed)}
            - APR: {APR_pct:.2f}% 
            - Monthly payment: {fmt_usd(m)}
            - Total interest: {fmt_usd(intr)}
            """
            st.download_button("Download short report (TXT)", data=report_md, file_name="heloc_summary.txt", mime="text/plain")

# --- Small responsive CSS tweaks (optional) -----------------------------------
# These tweaks improve readability on small screens (font size, padding).
st.markdown(
    """
    <style>
      /* reduce left/right padding on small screens */
      @media (max-width: 600px) {
        .reportview-container .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        h1 { font-size: 1.4rem; }
        h2 { font-size: 1.1rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)






