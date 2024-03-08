from next_move.games import PlayerColour
from next_move.openings.opening import Opening
from collections import defaultdict, Counter
from itertools import chain
from typing import Literal
from functools import reduce

import json
import numpy as np
import pandas as pd


class Tree:
    """
    Tree of Openings objects

    It is a graph object with the starting board FEN at the root, being the parent of all starting openings.
    An opening is a parent of another if there was a game in which the child followed the parent -- not
    necessarily in the following move, but immediately in terms of openings. This means that the graph is
    __not__ a DAG, because cycles can occur.

    Nodes:
        - The nodes are Opening objects

    Edges:
        - Edges is a dictionary of dictionaries of the form `{parent: {child: count}}`
        - The count is the number of times the child opening followed the parent opening
    """

    def __init__(self):
        self.nodes = {
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": Opening(
                fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
                name="Root",
                eco="ROOT",
                num_moves=0,
            )
        }
        self.edges: dict[str, dict[PlayerColour, Counter]] = defaultdict(
            lambda: defaultdict(Counter)
        )

    def __repr__(self):
        string_repr = ""

        for parent_node, children in self.edges.items():
            counter = {
                self.nodes[c]: count
                for c, count in reduce(lambda a, b: a | b, children.values()).items()
            }
            string_repr += f"{self.nodes[parent_node]} -> {counter}\n"

        return string_repr

    def partition_by_colour(self, colour: PlayerColour) -> "Tree":
        """Partitions the tree by colour"""
        tree = Tree()

        tree.nodes = tree.nodes | {
            k: v.partition_by_colour(colour)
            for k, v in self.nodes.items()
            if v.partition_by_colour(colour) is not None
        }

        tree.edges = {
            parent: {colour: children[colour]}
            for parent, children in self.edges.items()
        }

        return tree

    def add_opening(self, opening: Opening, head: Opening):
        if opening.fen in self.nodes:
            self.nodes[opening.fen] += opening
        else:
            self.nodes[opening.fen] = opening

        # TODO this is based on the assumption, that the opening colour is
        # the last colour in the list -- need to think if this is a good idea
        self.edges[head.fen][opening.colour[-1]][opening.fen] += 1

    def most_common_child(self, opening: Opening, n: int = 1):
        # TODO needs updating
        # return self.graph[opening].most_common(n)
        pass

    def to_sankey(self, prune_below_count: int = 0) -> dict[str, dict]:
        """Creates a Sankey diagram from the tree and saves in the provided path"""
        index_lookup = list(self.nodes.keys())
        labels = [f"{op.eco}" for op in self.nodes.values()]

        nodes = {
            "label": labels,
        }

        source, target, value = [], [], []
        for s, colour_counter in self.edges.items():
            t_counter = reduce(lambda a, b: a + b, colour_counter.values())
            for t, v in t_counter.items():
                if v < prune_below_count:
                    continue
                source.append(index_lookup.index(s))
                target.append(index_lookup.index(t))
                value.append(v)

        links = {
            "source": source,
            "target": target,
            "value": value,
        }

        return {"nodes": nodes, "links": links}

    def to_opening_strength(self) -> pd.DataFrame:
        """
        Creates a DataFrame of the strength of each opening

        The dataframe has a MultiIndex of the form (opening, number of moves, colour) and the following columns:
        - occurrence
        - mean following score
        - mean win rate
        - mean score in 5 moves
        """
        separator = ":::"
        all_nodes = list(self.nodes.values())
        rows = []

        for node in all_nodes:
            for c in [PlayerColour.W, PlayerColour.B]:
                c_opening = node.partition_by_colour(c)

                if c_opening is None:
                    continue

                rows.append(
                    (
                        f"{node.name}{separator}{node.num_moves}{separator}{c.value}",
                        np.mean(c_opening.following_game_scores),
                        np.mean(c_opening.results),
                        c_opening.occurrence,
                        c_opening.score_in_n_moves,
                    )
                )

        df = pd.DataFrame(
            columns=[
                "name",
                "mean_following_score",
                "mean_win_rate",
                "occurrence",
                "score_in_n_moves",
            ],
            data=rows,
        )

        df.set_index("name", inplace=True)

        df.set_index(
            df.index.str.split(separator, expand=True), inplace=True, drop=True
        )

        return df

    def to_timeline(self, breakdown: Literal["W", "M", "Y"] = "M") -> pd.DataFrame:
        """Creates a timeline of the openings in the tree, resampled by the breakdown period"""
        separator = ":::"
        all_nodes = list(self.nodes.values())

        df = pd.DataFrame(
            columns=["name", "fen", "date"],
            data=[
                (f"{node.name}{separator}{node.num_moves}", node.fen, date)
                for node in all_nodes
                for date in node.dates
            ],
        )

        df["first_name"] = df.groupby("fen")["name"].transform("first")

        def resample_and_merge(group: pd.DataFrame):
            resampled = (
                group.resample(breakdown, on="date").size().reset_index(name="count")  # type: ignore
            )
            resampled["name"] = group["first_name"].iloc[0]
            return resampled

        grouped = df.groupby("fen").apply(resample_and_merge).reset_index(drop=True)
        pivot_df = grouped.pivot_table(
            index="name", columns="date", values="count"
        ).fillna(0)

        pivot_df.set_index(
            pivot_df.index.str.split(separator, expand=True), inplace=True
        )

        return pivot_df

    def to_dict(self) -> dict:
        """Parses the object into a dict"""
        return {
            "nodes": {k: v.model_dump() for k, v in self.nodes.items()},
            "edges": self.edges,
        }

    def to_json(self, path: str) -> None:
        """Saves the tree as a JSON"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    @property
    def root(self):
        return self.nodes["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"]

    @classmethod
    def from_json(cls, path: str) -> "Tree":
        """Loads the tree from a JSON file"""
        with open(path, "r") as f:
            json_dict = json.load(f)

        tree = cls()
        tree.nodes = {
            fen: Opening(**opening) for fen, opening in json_dict["nodes"].items()
        }
        tree.edges = {
            parent: {
                PlayerColour.B if k == "B" else PlayerColour.W: Counter(v)
                for k, v in targets.items()
            }
            for parent, targets in json_dict["edges"]
        }

        return tree
