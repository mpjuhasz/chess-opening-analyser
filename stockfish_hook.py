# import chess
# from typing import Tuple
#
# sf_path = '/Users/Matyi/Desktop/BigBiz/nextMove/stockfish_12_win_x64_avx2/stockfish_20090216_x64_avx2.exe'
#
# print('Loading Stockfish 12...')
# engine = chess.engine.SimpleEngine.popen_uci(sf_path)
# print('Stockfish 12 ready')
#
# def stockfish_best_move(fen: str) -> Tuple[chess.engine.PovScore, str]:
#     board = chess.Board(fen=fen)
#     # TODO depth at 10, change it later
#     info = engine.analyse(board, chess.engine.Limit(depth=1))
#     return info['score'], info['pv'][0].uci()
