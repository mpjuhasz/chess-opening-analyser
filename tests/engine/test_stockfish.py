from next_move.engine.stockfish import Stockfish
from next_move.games import PlayerColour

import pytest


@pytest.mark.parametrize(
    ["fen", "colour", "expected"],
    [
        (
            "6Q1/p1p3P1/1k1p2N1/p1n1p2P/5r2/1b6/2n3q1/b4b1K w - - 32 32",
            PlayerColour.W,
            0.0,
        ),
        (
            "6Q1/p1p3P1/1k1p2N1/p1n1p2P/5r2/1b6/2n3q1/b4b1K w - - 32 32",
            PlayerColour.B,
            1.0,
        ),
        (
            "3R1bQR/p1k5/3p4/2n1p2P/3N1r2/1b4P1/1K1r4/b1q2b2 w - - 32 24",
            PlayerColour.W,
            0.0,
        ),
        (
            "3R1bQR/p1k5/3p4/2n1p2P/3N1r2/1b4P1/1K1r4/b1q2b2 w - - 32 24",
            PlayerColour.B,
            1.0,
        ),
    ],
)
def test_probability(fen: str, colour: PlayerColour, expected: float):
    stockfish = Stockfish("16/bin/stockfish", analysis_depth=20)
    move = stockfish.get_best_move(fen, colour)
    stockfish.quit()
    assert isinstance(move, dict)
    assert move["score"] == expected
