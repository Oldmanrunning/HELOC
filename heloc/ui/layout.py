from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from heloc.calculations.amortization import amortize_schedule
from heloc.calculations.monte_carlo import build_monte_carlo_interpretation, simulate_heloc_interest_rate_paths
from heloc.calculations.risk import calculate_risk_score, loan_to_value
from heloc.calculations.scenarios import build_scenario_comparison, choose_best_option, estimated_loan_amount
from heloc.reports.pdf_report import build_pdf_report
from heloc.services.ai_advisor import build_explanation_summary, get_ai_financial_explanation
from heloc.services.market_rates import get_market_rate_context
from heloc.visualizations.charts import render_balance_chart


APP_TITLE = "AI-Powered HELOC Financial Decision Intelligence Platform"


def apply_theme() -> None:
    """Apply portfolio-ready Streamlit styling."""
    st.markdown(
        """
        <style>
          :root {
            --heloc-navy: #0f172a;
            --heloc-blue: #2563eb;
            --heloc-sky: #dbeafe;
            --heloc-slate: #475569;
            --heloc-border: #e2e8f0;
          }
          .block-container {
            padding-top: 1.75rem;
            padding-bottom: 2.5rem;
          }
          .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 58%, #38bdf8 100%);
            border-radius: 1.5rem;
            padding: 2.25rem;
            margin-bottom: 1.5rem;
            color: white;
            box-shadow: 0 22px 55px rgba(15, 23, 42, 0.18);
          }
          .hero-card h1 {
            color: white;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.05;
            margin: 0 0 0.65rem 0;
            letter-spacing: -0.04em;
          }
          .hero-card p {
            color: rgba(255, 255, 255, 0.88);
            font-size: 1.05rem;
            max-width: 980px;
            margin-bottom: 1.25rem;
          }
          .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
          }
          .pill {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            color: white;
            font-weight: 650;
            font-size: 0.88rem;
          }
          div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--heloc-border);
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
          }
          div[data-testid="stTabs"] button p {
            font-weight: 650;
          }
          section[data-testid="stSidebar"] {
            background: #f8fafc;
          }
          @media (max-width: 700px) {
            .hero-card { padding: 1.35rem; border-radius: 1rem; }
            .block-container { padding-left: 1rem; padding-right: 1rem; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the application hero used by the main Streamlit entrypoint."""
    st.markdown(
        f"""
        <div class="hero-card">
          <h1>{APP_TITLE}</h1>
          <p>
            A portfolio-ready Streamlit decision platform for modeling HELOC payments,
            equity exposure, rate scenarios, Monte Carlo interest-rate uncertainty,
            and AI-assisted borrower-friendly explanations.
          </p>
          <div class="pill-row">
            <span class="pill">Risk Intelligence</span>
            <span class="pill">Scenario Modeling</span>
            <span class="pill">Monte Carlo Forecasting</span>
            <span class="pill">Exportable Reports</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app() -> None:
    """Render the complete HELOC Streamlit application."""
    from heloc.ui.inputs import render_inputs_form

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    render_hero()

    left_col, right_col = st.columns([0.95, 2.05], gap="large")

    with left_col:
        values = render_inputs_form()

    # Preserve the original single-file app behavior: show default results on
    # first load rather than leaving the dashboard blank before submission.
    if not values["calc_button"]:
        values["calc_button"] = True

    if values["calc_button"]:
        with right_col:
            render_results(values)


def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"


def render_results(values: dict) -> None:
    apr = values["APR_pct"] / 100.0
    apr_alt = values["APR_alt_pct"] / 100.0
    estimated_loan = estimated_loan_amount(values["Borrowed"], values["Existing_loan"])
    ltv = loan_to_value(estimated_loan, values["Home_value"])
    cltv = loan_to_value(values["Borrowed"] + values["Existing_loan"], values["Home_value"])

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

    st.subheader("Executive Decision Snapshot")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Monthly Payment", fmt_usd(m))
    k2.metric("Total Interest", fmt_usd(intr))
    k3.metric("Combined LTV", f"{cltv:.2%}")
    k4.metric("Risk Score", f"{risk['score']:.1f}/100", risk["level"])
    st.caption(
        "Use the tabs below to move from headline affordability to scenario stress tests, "
        "risk diagnostics, market context, and exportable documentation."
    )

    market_context = get_market_rate_context(values["APR_pct"])

    st.markdown("---")
    tabs = st.tabs(
        [
            "Overview",
            "Market Context",
            "Amortization",
            "Alternative APR",
            "Risk Intelligence",
            "Scenario Modeling",
            "Monte Carlo Forecast",
            "AI Financial Explanation",
            "Export",
        ]
    )

    with tabs[0]:
        st.header("Overview")
        st.markdown(
            "This section translates the borrower inputs into an at-a-glance decision brief "
            "for portfolio review, lender comparison, or financial planning discussions."
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                **Loan assumptions**
                - Requested draw: **{fmt_usd(values['Borrowed'])}**
                - HELOC APR: **{values['APR_pct']:.2f}%**
                - Repayment period: **{values['Period_years']} years**
                - Estimated combined loan amount: **{fmt_usd(estimated_loan)}**
                """
            )
        with c2:
            st.markdown(
                f"""
                **Equity and costs**
                - Home value: **{fmt_usd(values['Home_value'])}**
                - Existing liens: **{fmt_usd(values['Existing_loan'])}**
                - Combined LTV: **{cltv:.2%}**
                - Up-front / recurring fees modeled: **{fmt_usd(values['Application_fee'] + values['Annual_fee'] + values['Appraisal_fee'] + values['Origination_fee'] + values['Closing_costs'])}**
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
                    "Monthly_income": values["Monthly_income"],
                    "Monthly_debt": values["Monthly_debt"],
                }
            )
        st.info(risk["recommendation"])

    with tabs[1]:
        st.header("Market Context")
        st.markdown("Benchmark the entered APR against a prime-rate reference so the rate quote is easier to interpret.")
        m1, m2, m3 = st.columns(3)
        m1.metric(market_context.benchmark_label, f"{market_context.benchmark_rate:.2f}%")
        m2.metric("Date Retrieved", market_context.date_retrieved)
        m3.metric("Source", "Live" if market_context.is_live else "Sample/default")
        st.caption(market_context.source_label)
        st.markdown(f"**Comparison:** {market_context.comparison}")
        st.info(market_context.interpretation)

    with tabs[2]:
        st.header("Amortization schedule (first 24 months)")
        if sched.empty:
            st.info("No schedule (zero principal or period).")
        else:
            st.dataframe(sched.head(24).assign(payment=lambda df: df["payment"].map(fmt_usd)))
            render_balance_chart(sched)

    with tabs[3]:
        st.header("Compare to alternative APR")
        st.markdown(
            f"- **Alt APR:** {values['APR_alt_pct']:.2f}%  \n"
            f"- **Monthly (alt):** {fmt_usd(m_alt)}  \n"
            f"- **Total interest (alt):** {fmt_usd(intr_alt)}"
        )
        st.write("Difference in monthly payment:", fmt_usd(m_alt - m))
        st.write("Difference in total interest:", fmt_usd(intr_alt - intr))

    with tabs[4]:
        st.header("Risk Intelligence")
        st.markdown("A transparent rules-based score summarizes equity, term, APR, fee, and affordability signals.")
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

    with tabs[5]:
        st.header("Scenario Modeling")
        st.markdown("Stress-test the quote against rate changes, home-value declines, and alternative debt products.")
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

    with tabs[6]:
        st.header("Monte Carlo Forecast")
        st.caption(
            "Educational model: APR follows a random walk, and payments are re-amortized monthly "
            "over the remaining term at each simulated APR."
        )
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            mc_starting_apr_pct = st.number_input(
                "Starting APR for simulation (%)",
                min_value=0.0,
                value=float(values["APR_pct"]),
                step=0.05,
                format="%.2f",
            )
        with mc2:
            mc_volatility_pct = st.number_input(
                "Annual APR volatility (%)",
                min_value=0.0,
                value=2.0,
                step=0.1,
                format="%.2f",
                help="A value of 2.00 means annualized volatility of about two percentage points.",
            )
        with mc3:
            mc_simulations = st.number_input(
                "Number of simulations",
                min_value=1000,
                max_value=20000,
                value=5000,
                step=1000,
            )

        mc_result = simulate_heloc_interest_rate_paths(
            starting_apr=mc_starting_apr_pct / 100.0,
            annual_apr_volatility=mc_volatility_pct / 100.0,
            years=values["Period_years"],
            principal=values["Borrowed"],
            number_of_simulations=int(mc_simulations),
        )

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Median Total Interest", fmt_usd(mc_result["median_total_interest"]))
        f2.metric("10th Percentile", fmt_usd(mc_result["p10_total_interest"]))
        f3.metric("90th Percentile", fmt_usd(mc_result["p90_total_interest"]))
        f4.metric(
            "P(Interest > Baseline +10%)",
            f"{mc_result['probability_exceeds_baseline_by_10']:.1%}",
        )

        simulation_df = mc_result["simulation_df"]
        fig = px.histogram(
            simulation_df,
            x="total_interest",
            nbins=50,
            title="Distribution of Simulated Total Interest",
            labels={"total_interest": "Total Interest (USD)", "count": "Simulation Count"},
        )
        fig.add_vline(
            x=mc_result["baseline_total_interest"],
            line_dash="dash",
            line_color="red",
            annotation_text="Fixed-rate baseline",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            build_monte_carlo_interpretation(
                median_total_interest=mc_result["median_total_interest"],
                p10_total_interest=mc_result["p10_total_interest"],
                p90_total_interest=mc_result["p90_total_interest"],
                baseline_total_interest=mc_result["baseline_total_interest"],
                probability_exceeds_baseline_by_10=mc_result["probability_exceeds_baseline_by_10"],
            )
        )
        with st.expander("Model transparency"):
            st.markdown(
                f"""
                - **Starting APR:** {mc_starting_apr_pct:.2f}%
                - **Annual APR volatility:** {mc_volatility_pct:.2f} percentage points
                - **Years:** {values['Period_years']}
                - **Principal:** {fmt_usd(values['Borrowed'])}
                - **Simulations:** {int(mc_simulations):,}
                - **Baseline total interest:** {fmt_usd(mc_result['baseline_total_interest'])}
                """
            )
            st.dataframe(simulation_df.head(100), use_container_width=True)

    with tabs[7]:
        st.header("AI Financial Explanation")
        scenario_df_for_explainer = build_scenario_comparison(
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
        summary = build_explanation_summary(
            monthly_payment=m,
            monthly_income=values["Monthly_income"],
            ltv=ltv,
            cltv=cltv,
            risk=risk,
            scenario_df=scenario_df_for_explainer,
        )
        status_message, explanation = get_ai_financial_explanation(summary)
        st.caption(status_message)
        st.write(explanation)
        st.warning(
            "Disclaimer: This explanation is an educational planning aid and not financial advice. "
            "It excludes personally identifying information."
        )

    with tabs[8]:
        st.header("Export")
        st.write("Download the amortization schedule, a concise text summary, or a portfolio-ready PDF report.")
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
