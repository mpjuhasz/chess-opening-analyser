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
        return fig
