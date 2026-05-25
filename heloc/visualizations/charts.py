import streamlit as st
import pandas as pd


def render_balance_chart(schedule: pd.DataFrame) -> None:
    if not schedule.empty:
        st.line_chart(schedule.set_index("month")["balance"])
