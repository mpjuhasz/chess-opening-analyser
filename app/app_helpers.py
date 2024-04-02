from next_move.openings.transformers import Transformer
from next_move.visualiser.visualiser import Visualiser

import streamlit as st
import pandas as pd


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

        # family_or_opening = st.radio(
        #     "Show by",
        #     ("Family", "Opening"),
        # )

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
