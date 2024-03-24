from plotly import graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns


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
            ]
        )

        fig.update_layout(title_text="Openings tree", font_size=10)
        return fig

    @classmethod
    def timeline(cls, df: pd.DataFrame, move: int) -> Figure:
        """Takes a dataframe with the time points as columns, and openings as rows"""
        df = df.xs(move, level=1).div(df.xs(move, level=1).sum(axis=0))
        n, m = df.shape
        print(n, m)

        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(m * 0.25, n * 0.25))

        # df = df[df.apply(lambda x: max(x) > 0.05, axis=1)]

        df.columns = df.columns.strftime("%Y-%m-%d")  # type: ignore

        sns.heatmap(df, annot=False, cmap="YlGnBu", ax=ax, cbar=False, yticklabels=True)
        ax.set_xticklabels(
            ax.get_xticklabels(), rotation=45, horizontalalignment="right"
        )

        plt.legend(loc="upper right", bbox_to_anchor=(-0.05, 1))
        plt.tight_layout()
        return fig
