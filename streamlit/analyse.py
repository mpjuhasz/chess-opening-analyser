import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from cli.analyse_openings import run_analysis


st.title("Analyse chess games")
# input box for player id:
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
            with open("./tree.html", "r") as f:
                html = f.read()
            components.html(html, width=800, height=1000)
        elif option == "Timeline":
            # TODO this to be moved out into the visualiser
            df = pd.read_csv("timeline_2.csv", index_col=[0, 1])
            move = st.slider("Number of moves", 0, max(df.index.get_level_values(1)), 1)
            fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(12, 10))
            df = df.xs(move, level=1).div(df.xs(move, level=1).sum(axis=0))
            df = df[df.apply(lambda x: max(x) > 0.05, axis=1)]
            sns.heatmap(
                df, annot=False, cmap="YlGnBu", ax=ax[0], cbar=False, yticklabels=True
            )
            ax[0].set_xticklabels(
                ax[0].get_xticklabels(), rotation=45, horizontalalignment="right"
            )
            sns.lineplot(data=df.T, ax=ax[1])
            ax[1].set_xticklabels(
                ax[1].get_xticklabels(), rotation=45, horizontalalignment="right"
            )
            plt.legend(loc="upper right", bbox_to_anchor=(-0.05, 1))
            plt.tight_layout()
            st.pyplot(fig)
