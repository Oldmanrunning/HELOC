import streamlit as st

from heloc.ui.inputs import render_inputs_form
from heloc.ui.layout import render_results

st.set_page_config(page_title="HELOC Calculator", layout="wide")
st.title("HELOC Calculator")
st.caption("Responsive layout — works on desktop, tablet, and phones")

left_col, right_col = st.columns([1, 2])

with left_col:
    values = render_inputs_form()

if not values["calc_button"]:
    values["calc_button"] = True

if values["calc_button"]:
    with right_col:
        render_results(values)

st.markdown(
    """
    <style>
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
