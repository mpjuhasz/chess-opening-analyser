from collections import Counter
from datetime import datetime
from chess_opening_analyser.games import PlayerColour
from chess_opening_analyser.openings.tree import Tree
from chess_opening_analyser.openings.opening import Opening


def load_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
        index=1,
        num_moves=1,
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
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
        index=2,
        num_moves=1,
        colour=[PlayerColour.B],
        dates=[datetime.now()],
        results=[1],
        occurrence=1,
        following_moves=["b2b4"],
        following_game_scores=[0.21],
        score_in_n_moves=[0.1],
        best_next_move="c4d5",
    )

    tree.add_opening(first_opening, head=tree.root, player_colour=PlayerColour.W)
    tree.add_opening(second_opening, head=tree.root, player_colour=PlayerColour.B)
    return tree


def load_tree_2():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        index=1,
        name="King's pawn",
        num_moves=1,
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
        fen="rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
        eco="Sicilian Defense",
        name="Sicilian Defense",
        index=2,
        num_moves=2,
        colour=[PlayerColour.B, PlayerColour.W, PlayerColour.B],
        dates=[datetime.now(), datetime.now(), datetime.now()],
        results=[0, 1, 0.5],
        occurrence=3,
        following_moves=["d2d4", "d2d4", "d2d4"],
        following_game_scores=[0.21, 0.41, 0.12],
        score_in_n_moves=[0.13, 0.22, 0.1],
        best_next_move="d2d4",
    )
    third_opening = Opening(
        fen="rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2",
        eco="Scandinavian Defense",
        name="Scandinavian Defense",
        index=3,
        num_moves=2,
        colour=[PlayerColour.B, PlayerColour.W, PlayerColour.W],
        dates=[datetime.now(), datetime.now(), datetime.now()],
        results=[0.5, 0, 0],
        occurrence=3,
        following_moves=["d2d4", "d2d4", "d2d4"],
        following_game_scores=[0.44, 0.54, 0.12],
        score_in_n_moves=[0.04, 0.14, 0.43],
        best_next_move="d2d4",
    )
    tree.add_opening(first_opening, head=tree.root, player_colour=PlayerColour.W)
    tree.add_opening(second_opening, head=first_opening, player_colour=PlayerColour.B)
    tree.add_opening(third_opening, head=first_opening, player_colour=PlayerColour.W)

    # need to overwrite because of how the tree is created here
    tree.edges["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"] = {
        PlayerColour.W: Counter(
            {
                "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": 1,
                "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2": 2,
            }
        ),
        PlayerColour.B: Counter(
            {
                "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": 2,
                "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2": 1,
            }
        ),
    }

    return tree


def test_tree_add():
    fen_1 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    fen_2 = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"
    tree_1 = load_tree_2()
    tree_2 = load_tree_2()

    tree = tree_1 + tree_2

    assert tree.nodes[fen_1].occurrence == 2
    assert tree.edges[fen_1][PlayerColour.W][fen_2] == 4
    assert (
        tree.nodes[fen_2].colour == [PlayerColour.B, PlayerColour.W, PlayerColour.W] * 2
    )


def test_tree_add_2():
    fen_1 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"

    tree_1 = load_tree_2()
    tree_1.edges[fen_1].pop(PlayerColour.B)
    tree_2 = load_tree_2()
    tree_2.edges[fen_1].pop(PlayerColour.W)

    tree_sum = tree_1 + tree_2

    assert isinstance(tree_sum.edges[fen_1][PlayerColour.W], Counter)
    assert tree_sum.edges[fen_1][PlayerColour.W] == tree_1.edges[fen_1][PlayerColour.W]
    assert tree_sum.edges[fen_1][PlayerColour.B] == tree_2.edges[fen_1][PlayerColour.B]


def test_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
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

    tree.add_opening(first_opening, head=tree.root, player_colour=PlayerColour.W)

    assert tree.edges[tree.root.fen][PlayerColour.W][first_opening.fen] == 1
    assert tree.nodes[first_opening.fen] == first_opening


def test_partition_by_colour():
    tree = load_tree()
    white_tree = tree.partition_by_colour(PlayerColour.W)

    assert (
        tree.nodes[
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        ].occurrence
        == 2
    )
    assert (
        white_tree.nodes[
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        ].occurrence
        == 1
    )
    first_opening = tree.nodes[
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    ]
    assert first_opening in white_tree.nodes.values()
    assert first_opening.fen in white_tree.edges[tree.root.fen][PlayerColour.W]
    assert PlayerColour.B not in white_tree.edges[tree.root.fen].keys()


def test_children():
    tree = load_tree_2()

    assert (
        tree.children(tree.root.fen, PlayerColour.W)[0].fen
        == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    )
    assert tree.children(tree.root.fen, PlayerColour.B) == []
    assert len(tree.children(tree.root.fen)) == 1

    assert (
        tree.children(
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", PlayerColour.W
        )[0].fen
        == "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
    )
    assert (
        tree.children("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2")
        == []
    )
    assert set(
        [
            o.fen
            for o in tree.children(
                "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
            )
        ]
    ) == {
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
        "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2",
    }


def test_parents():
    tree = load_tree_2()

    assert (
        tree.parents("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")[
            0
        ].fen
        == tree.root.fen
    )

    assert (
        tree.parents("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2")[
            0
        ].fen
        == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    )
