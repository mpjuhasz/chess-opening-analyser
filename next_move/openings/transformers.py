from typing import Literal

import numpy as np
from next_move.games import PlayerColour
from next_move.openings.opening import Opening
from next_move.openings.tree import Tree

import pandas as pd


class Transformer:
    """Class to collect Tree transformations"""

    SEPARATOR = ":::"
    INDEX_NAMES = ["name", "move", "colour"]
    INDEX_TYPES = [str, int, str]

    @classmethod
    def tree_to_timeline(
        cls,
        tree: Tree,
        resample_interval: Literal["W", "M", "Y"] = "M",
        occurrence_threshold: int = 0,
    ) -> pd.DataFrame:
        """Creates a timeline of the openings in the tree, resampled by the breakdown period"""
        df = cls._tree_to_df(tree, ["dates"])
        df = df.explode("dates", ignore_index=True)

        def resample_and_merge(group: pd.DataFrame):
            resampled = (
                group.resample(resample_interval, on="dates").size().reset_index(name="count")  # type: ignore
            )
            return resampled

        grouped = df.groupby("name").apply(resample_and_merge)

        pivot_df = grouped.pivot_table(
            index="name", columns="dates", values="count"
        ).fillna(0)

        pivot_df = pivot_df[
            pivot_df.apply(lambda x: max(x) > occurrence_threshold, axis=1)
        ]

        pivot_df.index = cls._create_multi_index(pivot_df)

        return pivot_df

    @classmethod
    def to_opening_strength(cls, tree: Tree) -> pd.DataFrame:
        """
        Creates a DataFrame of the strength of each opening

        The dataframe has a MultiIndex of the form (opening, number of moves, colour) and the following columns:
        - occurrence
        - mean following score
        - mean win rate
        - mean score in 5 moves
        """

        df = cls._tree_to_df(
            tree,
            ["following_game_scores", "results", "occurrence", "score_in_n_moves"],
        )

        df["mean_following_score"] = df["following_game_scores"].apply(np.mean)
        df["mean_win_rate"] = df["results"].apply(np.mean)
        df["mean_score_in_n_moves"] = df["score_in_n_moves"].apply(np.mean)

        df.drop(
            ["following_game_scores", "results", "score_in_n_moves"],
            axis=1,
            inplace=True,
        )

        df.set_index("name", inplace=True)

        df.index = cls._create_multi_index(df)

        return df

    @classmethod
    def _create_multi_index(cls, df: pd.DataFrame) -> pd.MultiIndex:
        """From the index joined by SEPARATOR, creates a MultiIndex"""
        tuples = []
        for i in df.index:
            split = i.split(cls.SEPARATOR)
            tuples.append(tuple(map(lambda x, y: y(x), split, cls.INDEX_TYPES)))

        return pd.MultiIndex.from_tuples(
            tuples,
            names=cls.INDEX_NAMES,
        )

    @classmethod
    def _tree_to_df(cls, tree: Tree, attributes: list[str]) -> pd.DataFrame:
        """Transforms the tree to a DataFrame, with the standard name column as merged multi-index with name, move and colour"""
        all_nodes = list(tree.nodes.values())

        rows = []
        for node in all_nodes:
            for c in [PlayerColour.W, PlayerColour.B]:
                c_opening = node.partition_by_colour(c)

                if c_opening is None:
                    continue

                rows.append(
                    (
                        f"{node.name}{cls.SEPARATOR}{node.num_moves}{cls.SEPARATOR}{c.value}",
                        *(getattr(c_opening, a) for a in attributes),
                    )
                )

        return pd.DataFrame(
            columns=["name", *attributes],
            data=rows,
        )