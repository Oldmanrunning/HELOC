import streamlit as st

from heloc.ui.inputs import render_inputs_form
from heloc.ui.layout import render_results

APP_TITLE = "AI-Powered HELOC Financial Decision Intelligence Platform"


def apply_theme() -> None:
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


def main() -> None:
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

    if not values["calc_button"]:
        values["calc_button"] = True

    if values["calc_button"]:
        with right_col:
            render_results(values)


if __name__ == "__main__":
    main()
