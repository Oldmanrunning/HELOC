import streamlit as st


def render_inputs_form() -> dict:
    with st.form("inputs_form"):
        st.subheader("Borrower & Loan Assumptions")
        st.caption("Tune the inputs below to evaluate payment, equity, cost, and risk trade-offs.")

        borrowed = st.number_input(
            "Requested HELOC draw (USD)",
            min_value=0.0,
            max_value=200000.0,
            value=60000.0,
            step=1000.0,
            format="%.2f",
            help="The amount you plan to borrow or draw from the credit line.",
        )

        apr_pct = st.number_input(
            "HELOC APR (%)",
            min_value=0.0,
            value=8.5,
            step=0.01,
            format="%.2f",
            help="Enter the current or expected annual percentage rate.",
        )
        period_years = st.number_input(
            "Repayment period (years)",
            min_value=1,
            max_value=30,
            value=15,
            step=1,
        )

        st.divider()
        st.markdown("**Property & equity profile**")
        home_value = st.number_input(
            "Estimated home value (USD)",
            min_value=0.0,
            value=400000.0,
            step=1000.0,
            format="%.2f",
        )
        existing_loan = st.number_input(
            "Existing mortgage / liens (USD)",
            min_value=0.0,
            value=200000.0,
            step=1000.0,
            format="%.2f",
        )

        st.divider()
        st.markdown("**Fees & closing costs**")
        col_a, col_b = st.columns(2)
        with col_a:
            application_fee = st.number_input("Application fee", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            appraisal_fee = st.number_input("Appraisal fee", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            origination_fee = st.number_input("Origination fee", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        with col_b:
            annual_fee = st.number_input("Annual fee", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            closing_costs = st.number_input("Closing costs", min_value=0.0, value=0.0, step=10.0, format="%.2f")

        st.divider()
        st.markdown("**Comparison & affordability**")
        apr_alt_pct = st.number_input(
            "Alternative financing APR (%)",
            min_value=0.0,
            value=28.0,
            step=0.1,
            format="%.2f",
            help="Use this to compare against credit card, personal loan, or lender quote alternatives.",
        )
        monthly_income = st.number_input(
            "Monthly gross income (optional)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
        )
        monthly_debt = st.number_input(
            "Current monthly debt obligations (optional)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            format="%.2f",
        )
        calc_button = st.form_submit_button("Analyze HELOC Decision", use_container_width=True)

    return {
        "Borrowed": borrowed,
        "APR_pct": apr_pct,
        "Period_years": period_years,
        "Application_fee": application_fee,
        "Annual_fee": annual_fee,
        "Appraisal_fee": appraisal_fee,
        "Origination_fee": origination_fee,
        "Closing_costs": closing_costs,
        "Home_value": home_value,
        "Existing_loan": existing_loan,
        "APR_alt_pct": apr_alt_pct,
        "Monthly_income": monthly_income,
        "Monthly_debt": monthly_debt,
        "calc_button": calc_button,
    }
