from chess_opening_analyser.games import PlayerColour
from chess_opening_analyser.openings.opening import Opening
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
        - The nodes are dictionaries of the form `{fen: Opening}`

    Edges:
        - Edges is a dictionary of dictionaries of the form `{parent: {player_colour: {child: count}}`
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

    def filter_by_opening(self, opening_fen: str) -> "Tree":
        """
        Filters the tree by a specific opening

        Only children and downwards as well as parents and upwards are kept.
        """
        parents = self._get_parents_recursively(opening_fen)
        children = self._get_children_recursively(opening_fen)

        all_fens_to_keep = set(
            [opening_fen] + [o.fen for o in parents] + [o.fen for o in children]
        )

        nodes_to_keep = {k: v for k, v in self.nodes.items() if k in all_fens_to_keep}
        edges_to_keep = {k: v for k, v in self.edges.items() if k in all_fens_to_keep}
        edges_to_keep = self._prune_edges_by_target(all_fens_to_keep, edges_to_keep)

        tree = Tree()
        tree.nodes = nodes_to_keep
        tree.edges = edges_to_keep

        return tree

    @staticmethod
    def _prune_edges_by_target(
        nodes_to_keep: set[str], edges: dict[str, dict[PlayerColour, Counter]]
    ) -> dict[str, dict[PlayerColour, Counter]]:
        """Prunes the edges by the target"""
        return {
            parent: {
                colour: Counter(
                    {
                        child: count
                        for child, count in children.items()
                        if child in nodes_to_keep
                    }
                )
                for colour, children in targets.items()
            }
            for parent, targets in edges.items()
        }

    def _get_parents_recursively(
        self, opening_fen: str, colour: Optional[PlayerColour] = None
    ) -> list[Opening]:
        """Retrieves the parents of an opening recursively up to the root"""
        parents = self.parents(opening_fen, colour)
        for parent in parents:
            parents += self._get_parents_recursively(parent.fen, colour)
        return parents

    def _get_children_recursively(
        self, opening_fen: str, colour: Optional[PlayerColour] = None
    ) -> list[Opening]:
        """Retreives the children of an opening recursively down to the leaves"""
        children = self.children(opening_fen, colour)
        for child in children:
            children += self._get_children_recursively(child.fen, colour)
        return children

    def parents(
        self, opening_fen: str, colour: Optional[PlayerColour] = None
    ) -> list[Opening]:
        """
        Returns the heads of the opening

        NOTE: the opening can have multiple heads, from multiple levels. This is due to the
        possibility of transpositions.

        Args:
            opening_fen (str): The FEN of the opening
            colour (Optional[PlayerColour], optional): The colour to regard when searching for parents.
                If None, all parents are returned. Defaults to None.
        """
        parents = []

        for fen, child_counter in self.edges.items():
            if colour is None:
                tmp_d = reduce(lambda a, b: a + b, child_counter.values())
            else:
                tmp_d = child_counter[colour]

            if opening_fen in tmp_d:
                parents.append(self.nodes[fen])

        return parents

    def children(
        self, opening_fen: str, colour: Optional[PlayerColour] = None
    ) -> list[Opening]:
        """
        Returns the children of the opening

        Args:
            opening_fen (str): The FEN of the opening
            colour (Optional[PlayerColour], optional): The colour to regard when searching for children.
                If None, all children are returned. Defaults to None.
        """
        if opening_fen not in self.edges:
            return []
        if colour is None:
            return list(
                chain.from_iterable(
                    [
                        [self.nodes[f] for f in children]
                        for children in self.edges[opening_fen].values()
                    ]
                )
            )
        else:
            return [self.nodes[f] for f in self.edges[opening_fen][colour].keys()]

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
        """
        Partitions the tree by colour

        Returns a tree with only the openings that are played by the given colour (from
        the perspective of the user).
        """
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

    def add_opening(self, opening: Opening, head: Opening, player_colour: PlayerColour):
        """Adds an opening to the tree"""
        if opening.fen in self.nodes:
            self.nodes[opening.fen] += opening
        else:
            self.nodes[opening.fen] = opening

        self.edges[head.fen][player_colour][opening.fen] += 1

    def get_opening_by_name_and_move(self, name: str, move: int) -> Optional[Opening]:
        """Gets an opening by name and move"""
        for opening in self.nodes.values():
            if opening.name == name and opening.num_moves == move:
                return opening

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
