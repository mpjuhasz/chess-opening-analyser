from next_move.games import PlayerColour
from next_move.openings.opening import Opening
from datetime import datetime


def test_init_opening():
    op = Opening(
        eco="3042",
        fen="rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq -",
        name="Neo-Gr\u00fcnfeld Defense",
        num_moves=6,
    )

    op.update_opening(
        date=datetime.now(),
        result=0,
        colour=PlayerColour.W,
        following_move="c4d5",
        score=0.21,
        best_move="c4d5",
    )

    assert isinstance(op.following_moves, list)
    assert op.following_moves == ["c4d5"]
    assert op.occurrence == 1
    assert op.following_game_scores == [0.21]


def test_partitioning():
    op = Opening(
        eco="3042",
        fen="rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq -",
        name="Neo-Gr\u00fcnfeld Defense",
        num_moves=6,
        colour=[PlayerColour.W, PlayerColour.B],
        dates=[datetime.now(), datetime.now()],
        results=[0, 1],
        occurrence=2,
        following_moves=["c4d5", "c4d5"],
        following_game_scores=[0.41, 0.21],
        score_in_n_moves=[-0.1, 0.1],
        best_next_move="c4d5",
    )

    black_op = op.partition_by_colour(PlayerColour.B)

    assert isinstance(black_op, Opening)
    assert black_op.colour == [PlayerColour.B]
    assert black_op.results == [1]
    assert black_op.occurrence == 1
    assert black_op.following_moves == ["c4d5"]
    assert black_op.following_game_scores == [0.21]
