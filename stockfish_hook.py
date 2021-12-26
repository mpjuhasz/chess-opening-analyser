import chess
from typing import Tuple

sf_path = '/Users/Matyi/Desktop/BigBiz/nextMove/stockfish_12_win_x64_avx2/stockfish_20090216_x64_avx2.exe'

print('Loading Stockfish 12...')
engine = chess.engine.SimpleEngine.popen_uci(sf_path)
print('Stockfish 12 ready')


def stockfish_best_move(fen: str) -> Tuple[chess.engine.PovScore, str]:
    board = chess.Board(fen=fen)
    # TODO depth at 10, change it later
    info = engine.analyse(board, chess.engine.Limit(depth=1))
    return info['score'], info['pv'][0].uci()


def stockfish_probability(board: chess.Board, colour_played: str) -> float:
    """Gets the stockfish probability for win"""
    info = engine.analyse(board, chess.engine.Limit(time=1))
    return get_probability(info, colour_played)


def get_probability(info: dict, colour_played: str):
    if colour_played == 'W':
        return info['score'].white().wdl().wins / 1000 + info['score'].white().wdl().draws / 2000
    else:
        return info['score'].black().wdl().wins / 1000 + info['score'].black().wdl().draws / 2000
