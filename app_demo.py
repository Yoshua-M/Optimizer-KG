import streamlit as st

from optimizer.presentation.streamlit_demo_app import run_demo_app

st.set_page_config(
    page_title="Optimizer Demo",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
)

run_demo_app()
