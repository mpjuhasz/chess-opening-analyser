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

    assert isinstance(op.following_moves, dict)
    assert op.following_moves["c4d5"] == 1
    assert op.occurrence == 1
    assert op.following_game_scores == [0.21]
