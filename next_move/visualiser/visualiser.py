from plotly import graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import chess
from chess.svg import board, Arrow

from next_move.openings.opening import Opening


class Visualiser:
    @classmethod
    def sankey(cls, nodes: dict[str, list], links: dict[str, list]) -> go.Figure:
        """Sankey visualisation"""
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes["label"],
                    ),
                    link=dict(
                        source=links["source"],
                        target=links["target"],
                        value=links["value"],
                    ),
                )
            ],
            layout=go.Layout(
                title="Openings tree",
                font=dict(size=10),
                width=1500,
                height=500,
            ),
        )

        return fig

    @classmethod
    def timeline(cls, df: pd.DataFrame, move: int) -> Figure:
        """Takes a dataframe with the time points as columns, and openings as rows"""
        df = df.xs(move, level=1).div(df.xs(move, level=1).sum(axis=0))
        n, m = df.shape
        fig, ax = plt.subplots(figsize=(16, 4))

        df.columns = df.columns.strftime("%Y-%m-%d")  # type: ignore

        sns.heatmap(df, annot=False, cmap="YlGnBu", ax=ax, cbar=False, yticklabels=True)
        ax.set_xticklabels(
            ax.get_xticklabels(), rotation=45, horizontalalignment="right"
        )

        plt.legend(loc="upper right", bbox_to_anchor=(-0.05, 1))
        plt.tight_layout()
        return fig

    @classmethod
    def board_from_opening(cls, opening: Opening) -> str:
        """Creates a board visualisation with following moves from an opening object"""
        b = chess.Board(opening.fen)

        arrows = []
        for move in opening.following_moves:
            if move:
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

        return board(
            b,
            arrows=arrows,
            size=600,
        )
