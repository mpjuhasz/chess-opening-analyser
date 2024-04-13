from typing import Literal
from chess_opening_analyser.games import PlayerColour
from chess_opening_analyser.openings.opening import Opening
from chess_opening_analyser.openings.transformers import Transformer
from chess_opening_analyser.visualiser.visualiser import Visualiser

import streamlit as st
import pandas as pd
import re


def color_value(val):
    r = 255 - int(75 * val)
    g = 200 + int(55 * val)
    b = 255
    return f"background-color: rgb({r},{g},{b})"


def timeline_page(player_id: str):
    """Creates the timeline page with the heatmap of opening ratios"""
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
        occurrence_threshold = st.slider("Minimum number of occurrences", 0, 100, 5)

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


def opening_strength_page(player_id: str):
    """Creates the opening strength page with the table of opening strengths"""
    df = Transformer.tree_to_opening_strength(
        st.session_state.trees[player_id], unique_names=True
    )

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


def single_opening_page(player_id):
    """Creates the single opening page"""
    df = Transformer.tree_to_opening_strength(
        st.session_state.trees[player_id], unique_names=False
    )

    opening_families = sorted(
        set(
            re.sub(r"\[[^\]]*\]", "", of.split(":")[0]).strip()
            for of in df.index.get_level_values(0)
        )
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
                    index=0,
                )
            with col2:
                next_move_mode = st.selectbox(
                    "Choose next-move vis",
                    ("DataFrame", "Plot"),
                    index=0,
                )

            assert move is not None  # mollify pyright
            opening = st.session_state.trees[player_id].get_opening_by_name_and_move(
                name, move
            )

            opening = opening.partition_by_colour(
                PlayerColour.B if move % 2 == 1 else PlayerColour.W
            )

            if opening and next_move_mode is not None:  # mollify pyright
                _single_opening_visuals(opening, player_id, next_move_mode)
            else:
                st.write("There are no games where it was your turn at this move.")


def _single_opening_visuals(
    opening: Opening, player_id: str, next_move_mode: Literal["DataFrame", "Plot"]
):
    """
    Creates the visualisations for the single opening page

    These currently include:
    - The board at the opening with arrows for the following moves
    - A table or scatter-plot of the following moves with their scores
    - A sankey diagram of the openings leading up to this one and following from it
    """
    board_string = Visualiser.board_from_opening(opening)

    col1, col2 = st.columns(2)

    with col1:
        st.image(board_string, use_column_width=True)

    with col2:
        score_cols = [
            "results",
            "score_in_n_moves",
            "following_game_scores",
        ]

        move_df = pd.DataFrame(
            {
                **{
                    sc: getattr(opening, sc)
                    for sc in score_cols + ["dates", "following_moves"]
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

    filtered_tree = st.session_state.trees[player_id].filter_by_opening(opening.fen)

    fig = Visualiser.sankey(**Transformer.tree_to_sankey(filtered_tree))
    st.plotly_chart(fig, use_container_width=True)
