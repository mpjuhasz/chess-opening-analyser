from next_move.engine.stockfish import Stockfish


def test_probability():
    stockfish = Stockfish("/Users/Matyi/git/nextMove/16/bin/stockfish", analysis_depth=20)
    move = stockfish.get_best_move("rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq -")
    assert isinstance(move, dict)
    assert move["move"] == 'c4d5'
