import streamlit as st
from cli.analyse_openings import run_analysis
from app.app_helpers import (
    timeline_page,
    opening_strength_page,
    single_opening_page,
)

st.set_page_config(layout="wide")
st.title("Analyse chess games")

player_id = st.text_input("Enter player id")

if "trees" not in st.session_state:
    st.session_state.trees = {}

if player_id:
    if player_id not in st.session_state.trees:
        with st.spinner("Analysing games..."):
            st.session_state.trees[player_id] = run_analysis(player_id)

    if st.session_state.trees:
        option = st.selectbox(
            "Choose visualisation",
            ("Timeline", "Opening strength", "Single opening"),
        )
        if option == "Timeline":
            timeline_page(player_id)
        elif option == "Opening strength":
            opening_strength_page(player_id)
        elif option == "Single opening":
            single_opening_page(player_id)
