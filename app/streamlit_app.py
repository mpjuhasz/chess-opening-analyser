import streamlit as st
import chess
import pandas as pd
from chess.svg import board, Arrow

from next_move.games import PlayerColour
from next_move.visualiser.visualiser import Visualiser
from next_move.openings.transformers import Transformer
from cli.analyse_openings import run_analysis
from app.app_helpers import color_value

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
            col1, col2 = st.columns(2)
            with col1:
                resample_interval = st.selectbox(
                    "Choose breakdown period",
                    ("W", "M", "Y"),
                )
                colour = st.selectbox(
                    "Choose colour",
                    ("Black", "White", "Both"),
                )
            with col2:
                occurrence_threshold = st.slider(
                    "Minimum number of occurrences", 0, 100, 5
                )

            assert resample_interval is not None

            df = Transformer.tree_to_timeline(
                st.session_state.trees[player_id],
                resample_interval=resample_interval,
                occurrence_threshold=occurrence_threshold,
            )

            if colour != "Both":
                df = df.xs(colour, level=2)
            else:
                df = df.groupby(level=[0, 1]).sum()

            move = st.slider(
                "Number of moves", 0, max(df.index.get_level_values(1).astype(int)), 1
            )
            assert isinstance(df, pd.DataFrame)
            fig = Visualiser.timeline(df, move)
            st.pyplot(fig)
        elif option == "Opening strength":
            df = Transformer.to_opening_strength(st.session_state.trees[player_id])

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
                n_moves = st.slider("Number of moves", 0, df.index.levels[1].max(), 1)  # type: ignore
                minimum_occurrence = st.slider("Minimum occurrence", 0, 100, 5)
                order_by = st.selectbox(
                    "Order by column",
                    df.columns,
                )

            st.table(
                df[df["occurrence"] > minimum_occurrence]
                .xs(n_moves, level=1)
                .xs(colour, level=1)
                .sort_values(order_by, ascending=strong_or_weak == "Weak")
                .style.applymap(
                    color_value,
                    subset=list(set(df.columns) - {"occurrence"}),
                )
            )
        elif option == "Single opening":
            df = Transformer.to_opening_strength(st.session_state.trees[player_id])

            name = st.selectbox(
                "Choose opening",
                df.index.levels[0],  # type: ignore
            )
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

                        board_string = Visualiser.board_from_opening(opening)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(
                                board_string,
                                unsafe_allow_html=True,
                            )

                        with col2:
                            score_cols = [
                                "results",
                                "score_in_n_moves",
                                "following_game_scores",
                            ]

                            move_df = pd.DataFrame(
                                {
                                    "following_moves": opening.following_moves,
                                    **{sc: getattr(opening, sc) for sc in score_cols},
                                    "occurrence": 1,
                                },
                            )

                            move_df = (
                                move_df.groupby("following_moves")
                                .agg(
                                    {
                                        **{sc: "mean" for sc in score_cols},
                                        "occurrence": "sum",
                                    }
                                )
                                .sort_values(by="occurrence", ascending=False)  # type: ignore
                            )

                            st.table(
                                move_df.style.applymap(
                                    color_value,
                                    subset=score_cols,
                                )
                            )

                        filtered_tree = st.session_state.trees[
                            player_id
                        ].filter_by_opening(opening.fen)

                        fig = Visualiser.sankey(**filtered_tree.to_sankey())
                        st.plotly_chart(fig)

                    else:
                        st.write(
                            "There are no games where it was your turn at this move."
                        )
