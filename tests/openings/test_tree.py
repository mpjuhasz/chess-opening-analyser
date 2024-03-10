from datetime import datetime
from next_move.games import PlayerColour
from next_move.openings.tree import Tree
from next_move.openings.opening import Opening


def test_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
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

    tree.add_opening(first_opening, head=tree.root)

    assert tree.edges[tree.root.fen][PlayerColour.W][first_opening.fen] == 1
    assert tree.nodes[first_opening.fen] == first_opening


def test_partition_by_colour():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
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
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
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

    tree.add_opening(first_opening, head=tree.root)
    tree.add_opening(second_opening, head=tree.root)
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
    assert first_opening in white_tree.nodes.values()
    assert first_opening.fen in white_tree.edges[tree.root.fen][PlayerColour.W]
    assert PlayerColour.B not in white_tree.edges[tree.root.fen].keys()


def test_most_common_child():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
        num_moves=1,
        colour=[PlayerColour.W],
        dates=[datetime.now()],
        results=[0],
        occurrence=1,
        following_moves=["c4d5"],
        following_game_scores=[0.41],
        best_next_move="c4d5",
    )

    tree.add_opening(first_opening, head=tree.root)
    # TODO needs updating
    # assert tree.most_common_child(tree.root, 1) == [(first_opening, 1)]
