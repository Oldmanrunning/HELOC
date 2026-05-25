import streamlit as st


def render_inputs_form() -> dict:
    with st.form("inputs_form"):
        st.header("Inputs")
        borrowed = st.slider("Borrowed (USD)", min_value=0.0, max_value=200000.0, value=50000.0, step=100.0, format="%.0f")
        borrowed_exact = st.number_input("Borrowed (exact)", value=borrowed, step=100.0, format="%.2f")
        if borrowed_exact != borrowed:
            borrowed = borrowed_exact

        apr_pct = st.number_input("HELOC APR (%)", min_value=0.0, value=8.5, step=0.01, format="%.2f")
        period_years = st.slider("Payment Period (years)", 1, 30, 10)

        st.write("**Fees & other values**")
        col_a, col_b = st.columns(2)
        with col_a:
            application_fee = st.number_input("Application Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            appraisal_fee = st.number_input("Appraisal Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            origination_fee = st.number_input("Origination Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        with col_b:
            annual_fee = st.number_input("Annual Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            closing_costs = st.number_input("Closing Costs (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")

        home_value = st.number_input("Home Value (USD)", min_value=0.0, value=400000.0, step=1000.0, format="%.2f")
        existing_loan = st.number_input("Existing Loan (USD)", min_value=0.0, value=200000.0, step=1000.0, format="%.2f")

        apr_alt_pct = st.number_input("Alternative APR (%)", min_value=0.0, value=28.0, step=0.1, format="%.2f")
        calc_button = st.form_submit_button("Calculate")

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
        "calc_button": calc_button,
    }
