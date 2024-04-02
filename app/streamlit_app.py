import streamlit as st
import chess
import pandas as pd
from chess.svg import board, Arrow

from next_move.games import PlayerColour
from next_move.visualiser.visualiser import Visualiser
from next_move.openings.transformers import Transformer
from cli.analyse_openings import run_analysis
from app.app_helpers import color_value, timeline_page, opening_strength_page

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
            df = Transformer.to_opening_strength(st.session_state.trees[player_id])

            opening_families = sorted(
                set(of.split(":")[0] for of in df.index.get_level_values(0))
            )

            family = st.selectbox(
                "Choose opening family",
                opening_families,
            )

            if family:
                df = df[df.index.get_level_values(0).str.startswith(family)]

                name = st.selectbox(
                    "Choose opening",
                    sorted(df.index.get_level_values(0).unique()),  # type: ignore
                )
                if name:
                    _df = df.xs(name, level=0)

                    col1, col2 = st.columns(2)
                    with col1:
                        move = st.selectbox(
                            "Choose move",
                            _df.index.get_level_values(0).unique(),
                        )
                    with col2:
                        next_move_mode = st.selectbox(
                            "Choose next-move vis", ("DataFrame", "Plot")
                        )

                    if move:
                        opening = st.session_state.trees[
                            player_id
                        ].get_opening_by_name_and_move(name, move)

                        opening = opening.partition_by_colour(
                            PlayerColour.B if move % 2 == 1 else PlayerColour.W
                        )

                        if opening:
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
                                    # "dates",
                                ]

                                move_df = pd.DataFrame(
                                    {
                                        "following_moves": opening.following_moves,
                                        **{
                                            sc: getattr(opening, sc)
                                            for sc in score_cols + ["dates"]
                                        },
                                        "occurrence": 1,
                                    },
                                )

                                if next_move_mode == "DataFrame":
                                    move_df.drop("dates", axis=1, inplace=True)
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
                                else:
                                    move_df = move_df.explode("dates")
                                    fig = Visualiser.scatter_from_next_moves(move_df)
                                    st.pyplot(fig)

                            filtered_tree = st.session_state.trees[
                                player_id
                            ].filter_by_opening(opening.fen)

                            fig = Visualiser.sankey(**filtered_tree.to_sankey())
                            st.plotly_chart(fig)

                        else:
                            st.write(
                                "There are no games where it was your turn at this move."
                            )
