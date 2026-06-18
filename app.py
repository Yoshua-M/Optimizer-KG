import streamlit as st

from optimizer.presentation.streamlit_app import run_app

st.set_page_config(
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

run_app()
