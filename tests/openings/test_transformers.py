from datetime import datetime
from chess_opening_analyser.games import PlayerColour
from chess_opening_analyser.openings.opening import Opening
from chess_opening_analyser.openings.transformers import Transformer
from chess_opening_analyser.openings.tree import Tree

import pandas as pd


def load_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="C20",
        name="King's pawn",
        num_moves=1,
        index=1,
        colour=[PlayerColour.W],
        dates=[datetime.now()],
        results=[0],
        occurrence=1,
        following_moves=["c4d5"],
        following_game_scores=[0.41],
        score_in_n_moves=[-0.1],
        best_next_move="c4d5",
    )
    second_opening = Opening(
        eco="D70",
        fen="rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq -",
        name="Neo-Gr\u00fcnfeld Defense",
        num_moves=6,
        index=2,
        colour=[PlayerColour.W, PlayerColour.B, PlayerColour.B, PlayerColour.W],
        dates=[
            datetime.now(),
            datetime(2022, 1, 1),
            datetime(2022, 1, 16),
            datetime(2023, 10, 10),
        ],
        results=[0, 1, 0, 0.5],
        occurrence=4,
        following_moves=["c4d5", "c4d5", "c4d5", "c4d5"],
        following_game_scores=[0.41, 0.21, 0.41, 0.21],
        score_in_n_moves=[-0.1, 0.1, -0.1, 0.1],
        best_next_move="c4d5",
    )
    tree.add_opening(first_opening, head=tree.root, player_colour=PlayerColour.W)
    tree.add_opening(second_opening, head=tree.root, player_colour=PlayerColour.W)
    return tree


def test_tree_to_timeline():
    tree = load_tree()

    timeline = Transformer.tree_to_timeline(
        tree, resample_interval="Y", occurrence_threshold=0
    )

    assert timeline.shape == (3, 3)
    assert timeline.columns.tolist() == [
        datetime(2022, 12, 31),
        datetime(2023, 12, 31),
        datetime(2024, 12, 31),
    ]

    assert isinstance(timeline.index, pd.MultiIndex)
    assert timeline.index.names == ["name", "move", "colour"]
    assert timeline.index.levels[0].tolist() == ["King's pawn [1]", "Neo-Grünfeld Defense [2]"]  # type: ignore
    assert (
        timeline.loc[("Neo-Grünfeld Defense [2]", 6, "Black")][datetime(2022, 12, 31)]
        == 2.0
    )


def test_tree_to_opening_strength():
    tree = load_tree()

    opening_strength = Transformer.to_opening_strength(tree)

    assert opening_strength.shape == (3, 4)
    assert opening_strength.columns.tolist() == [
        "occurrence",
        "mean_following_game_scores",
        "mean_results",
        "mean_score_in_n_moves",
    ]
    assert (
        opening_strength.loc[(("Neo-Grünfeld Defense [2]", 6, "Black"))]["occurrence"]
        == 2
    )
    assert (
        opening_strength.loc[(("Neo-Grünfeld Defense [2]", 6, "Black"))][
            "mean_following_game_scores"
        ]
        == 0.31
    )
    assert (
        opening_strength.loc[(("Neo-Grünfeld Defense [2]", 6, "Black"))]["mean_results"]
        == 0.50
    )
