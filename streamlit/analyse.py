import numpy as np
import streamlit as st
import chess
import pandas as pd
from chess.svg import board, Arrow

from next_move.games import PlayerColour
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
                colour = st.selectbox(
                    "Choose colour",
                    ("Black", "White", "Both"),
                )
            with col2:
                occurrence_threshold = st.slider(
                    "Minimum number of occurrences", 0, 100, 5
                )
            df = st.session_state.trees[player_id].to_timeline(
                breakdown=breakdown, occurrence_threshold=occurrence_threshold
            )

            if colour != "Both":
                df = df.xs(colour, level=2)

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
            # col1, col2 = st.columns(2)

            # with col1:
            name = st.selectbox(
                "Choose opening",
                df.index.levels[0],
            )

            # with col2:
            if name:
                _df = df.xs(name, level=0)

                move = st.selectbox(
                    "Choose move",
                    _df.index.get_level_values(0).unique(),
                )

                if move:
                    opening = st.session_state.trees[
                        player_id
                    ].get_opening_by_name_and_move(name, move)

                    opening = opening.partition_by_colour(
                        PlayerColour.B if move % 2 == 1 else PlayerColour.W
                    )

                    if opening:
                        st.write(opening.dict())

                        b = chess.Board(opening.fen)

                        arrows = []
                        for move in opening.following_moves:
                            arrows.append(
                                Arrow(
                                    chess.parse_square(move[:2]),
                                    chess.parse_square(move[2:]),
                                    color="#D3D3D38F",
                                )
                            )

                        arrows.append(
                            Arrow(
                                chess.parse_square(opening.best_next_move[:2]),
                                chess.parse_square(opening.best_next_move[2:]),
                                color="#008F008F",
                            )
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(
                                board(
                                    b,
                                    arrows=arrows,
                                    size=600,
                                ),
                                unsafe_allow_html=True,
                            )

                        with col2:
                            move_df = pd.DataFrame(
                                {
                                    "following_moves": opening.following_moves,
                                    "results": opening.results,
                                    "score_in_n_moves": opening.score_in_n_moves,
                                    "following_game_scores": opening.following_game_scores,
                                    "occurrence": 1,
                                },
                            )

                            move_df = (
                                move_df.groupby("following_moves")
                                .agg(
                                    {
                                        "results": "mean",
                                        "score_in_n_moves": "mean",
                                        "following_game_scores": "mean",
                                        "occurrence": "sum",
                                    }
                                )
                                .sort_values(by="occurrence", ascending=False)  # type: ignore
                            )

                            def color_value(val):
                                r = 255 - int(75 * val)
                                g = 200 + int(55 * val)
                                b = 255
                                return f"background-color: rgb({r},{g},{b})"

                            st.table(
                                move_df.style.applymap(
                                    color_value,
                                    subset=[
                                        "results",
                                        "score_in_n_moves",
                                        "following_game_scores",
                                    ],
                                )
                            )
                    else:
                        st.write(
                            "There are no games where it was your turn at this move."
                        )
