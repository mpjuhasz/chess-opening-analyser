from next_move.openings.opening import Opening
from collections import defaultdict, Counter
from tqdm import tqdm
from pathlib import Path

# import matplotlib.pyplot as plt
# from matplotlib.sankey import Sankey
import plotly.graph_objects as go
import json


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
                eco="ROOT    ",
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

    def to_sankey(self, path: str) -> None:
        """Creates a Sankey diagram from the tree and saves in the provided path"""
        index_lookup = list(self.nodes.keys())
        labels = [f"{op.eco}: {op.name}" for op in self.nodes.values()]

        nodes = {
            "label": labels,
        }

        source, target, value = [], [], []
        for s, t_counter in self.edges.items():
            source.append(index_lookup.index(s))
            for t, v in t_counter.items():
                target.append(index_lookup.index(t))
                value.append(v)

        links = {
            "source": source,
            "target": target,
            "value": value,
        }

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
        fig.write_html(path)

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
