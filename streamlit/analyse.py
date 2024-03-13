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
            ("Sankey", "Timeline", "Opening strength", "Single opening"),
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
        elif option == "Opening strength":
            df = st.session_state.trees[player_id].to_opening_strength()
            df["mean_score_in_n_moves"] = df["score_in_n_moves"].apply(
                lambda x: sum(x) / len(x)
            )
            df.drop("score_in_n_moves", axis=1, inplace=True)

            col1, col2 = st.columns(2)
            with col1:
                colour = st.selectbox(
                    "Choose colour",
                    ("Black", "White"),
                )
                strong_or_weak = st.radio(
                    "Show top openings by",
                    ("Strong", "Weak"),
                )

            with col2:
                n_moves = st.slider("Number of moves", 0, df.index.levels[1].max(), 1)
                minimum_occurrence = st.slider("Minimum occurrence", 0, 100, 5)
                order_by = st.selectbox(
                    "Order by column",
                    (
                        "mean_following_score",
                        "mean_win_rate",
                        "mean_score_in_n_moves",
                        "occurrence",
                    ),
                )

            st.table(
                df[df["occurrence"] > minimum_occurrence]
                .xs(n_moves, level=1)
                .xs(colour, level=1)
                .sort_values(order_by, ascending=strong_or_weak == "Weak")
                .head(20)
            )
        elif option == "Single opening":
            df = st.session_state.trees[player_id].to_opening_strength()
            col1, col2 = st.columns(2)

            with col1:
                name = st.selectbox(
                    "Choose opening",
                    df.index.levels[0],
                )

            with col2:
                _df = df.xs(name, level=0)
                move = st.selectbox(
                    "Choose move",
                    _df.index.levels[0],
                )

            opening = st.session_state.trees[player_id].get_opening_by_name_and_move(
                name, move
            )

            if opening:
                st.write(opening.dict())
