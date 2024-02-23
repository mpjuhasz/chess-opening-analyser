from next_move.openings.opening import Opening
from collections import defaultdict, Counter
from itertools import chain
from typing import Literal
from functools import reduce

import json
import pandas as pd


class Tree:
    """
    Tree of Openings objects

    It is a graph object with the starting board FEN at the root, being the parent of all starting openings.
    An opening is a parent of another if there was a game in which the child followed the parent -- not
    necessarily in the following move, but immediately in terms of openings. This means that the graph is
    __not__ a DAG, because cycles can occur.
    """

    def __init__(self):
        self.nodes = {
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": Opening(
                fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
                name="Root",
                eco="ROOT",
                num_moves=0
            )
        }
        self.edges = defaultdict(Counter)

    def __repr__(self):
        string_repr = ""

        for parent_node, children in self.edges.items():
            counter = {self.nodes[c]: count for c, count in children.items()}
            string_repr += f"{self.nodes[parent_node]} -> {counter}\n"

        return string_repr

    def add_opening(self, opening: Opening, head: Opening):
        if opening.fen in self.nodes:
            self.nodes[opening.fen] += opening
        else:
            self.nodes[opening.fen] = opening

        self.edges[head.fen][opening.fen] += 1

    def most_common_child(self, opening: Opening, n: int = 1):
        return self.graph[opening].most_common(n)

    def to_sankey(self, prune_below_count: int = 0) -> dict[str, dict]:
        """Creates a Sankey diagram from the tree and saves in the provided path"""
        index_lookup = list(self.nodes.keys())
        labels = [f"{op.eco}: {op.name}" for op in self.nodes.values()]

        nodes = {
            "label": labels,
        }

        source, target, value = [], [], []
        for s, t_counter in self.edges.items():
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

    def to_timeline(
        self, prune_below_count: int = 0, breakdown: Literal["W", "M", "Y"] = "M"
    ) -> pd.DataFrame:
        all_nodes = list(self.nodes.values())

        df = pd.DataFrame(
            columns=["name", "fen", "date"],
            data=[
                (f"{node.name} [{node.num_moves}]", node.fen, date) for node in all_nodes for date in node.dates
            ],
        )
        
        blank_df = pd.DataFrame(
            columns=["date", "name", "fen"],
            data={"date": pd.date_range(df["date"].min(), df["date"].max(), freq=breakdown)}
        )


        opening_counts = []
        df["first_name"] = df.groupby("fen")["name"].transform("first")

        for fen, group in df.groupby("fen"):
            group = group.set_index("date").resample(breakdown).count()
            group["name"] = df.loc[df["fen"] == fen].iloc[0]["first_name"]
            group.drop(columns=["fen"], inplace=True)
            opening_counts.append(group)
        
        df = reduce(
            lambda left, right: pd.merge(
                left,
                right,
                how="outer",
                on="date",
                suffixes=["", f"_{right['name'].iloc[0]}"],
            ),
            [blank_df] + opening_counts,
        )
        df = df.rename(columns={col: col.replace('first_name_', '') for col in df.columns})
        df.drop(columns=["name", "first_name", "fen"], inplace=True)  # cleaning up ccolumns from merging with blank
        return df.drop(columns=df.filter(regex="^name_").columns)

    def to_dict(self) -> dict:
        """Parses the object into a dict"""
        return {"nodes": {k: v.dict() for k, v in self.nodes}, "edges": self.edges}

    def to_json(self, path: str) -> None:
        """Saves the tree as a JSON"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), path)

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
            parent: Counter(targets) for parent, targets in json_dict["edges"]
        }

        return tree
