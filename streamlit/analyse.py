import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from next_move.visualiser.visualiser import Visualiser
from cli.analyse_openings import run_analysis

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
            ("Sankey", "Timeline"),
        )
        if option == "Sankey":
            fig = Visualiser.sankey(**st.session_state.trees[player_id].to_sankey())
            st.plotly_chart(fig)
        elif option == "Timeline":
            col1, col2 = st.columns(2)
            with col1:
                breakdown = st.selectbox(
                    "Choose breakdown period",
                    ("M", "W", "D"),
                )
            with col2:
                occurrence_threshold = st.slider(
                    "Minimum number of occurrences", 0, 100, 5
                )
            df = st.session_state.trees[player_id].to_timeline(
                breakdown=breakdown, occurrence_threshold=occurrence_threshold
            )
            move = st.slider(
                "Number of moves", 0, max(df.index.get_level_values(1).astype(int)), 1
            )
            fig = Visualiser.timeline(df, move)
            st.pyplot(fig)
