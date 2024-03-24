from next_move.games import PlayerColour
from next_move.openings.opening import Opening
from collections import defaultdict, Counter
from itertools import chain
from typing import Literal, Optional
from functools import reduce

import json
import numpy as np
import pandas as pd
from datetime import datetime


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

    def get_opening_by_name_and_move(self, name: str, move: int) -> Optional[Opening]:
        """Gets an opening by name and move"""
        for opening in self.nodes.values():
            if opening.name == name and opening.num_moves == move:
                return opening

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

    def to_dict(self) -> dict:
        """Parses the object into a dict"""
        return {
            "nodes": {k: v.model_dump() for k, v in self.nodes.items()},
            "edges": self.edges,
        }

    def to_json(self, path: str) -> None:
        """Saves the tree as a JSON"""
        with open(path, "w") as f:
            json.dump(
                self.to_dict(),
                f,
                default=lambda x: x.isoformat() if isinstance(x, datetime) else x,
            )

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
            fen: Opening(
                **{
                    **opening,
                    "dates": [datetime.fromisoformat(d) for d in opening["dates"]],
                    "colour": [PlayerColour(c) for c in opening["colour"]],
                }
            )
            for fen, opening in json_dict["nodes"].items()
        }
        tree.edges = {
            parent: {PlayerColour(k): Counter(v) for k, v in targets.items()}
            for parent, targets in json_dict["edges"].items()
        }

        return tree
