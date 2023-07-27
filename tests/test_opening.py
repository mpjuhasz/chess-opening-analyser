from next_move.opening import Opening
from datetime import datetime


def test_init_opening():
    op = Opening(
        eco="3042",
        fen="rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq -",
    )

    op.update_opening(
        date=datetime.now(),
        win=False,
        following_move="c4d5",
        following_game_score=0.21,
    )

    assert isinstance(op.following_moves, dict)
    assert op.following_moves["c4d5"] == 1
    assert op.occurrence == 1
    assert op.win_number == 0
    assert op.following_game_scores == [0.21]
