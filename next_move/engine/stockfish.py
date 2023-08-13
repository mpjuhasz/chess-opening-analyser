from chess import Board, engine
from pathlib import Path


class Stockfish:
    def __init__(self, stockfish_path: str | Path, analysis_depth=10):
        self.engine = engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = analysis_depth

    def get_best_move(self, fen: str):
        board = Board(fen=fen)
        stockfish_analysis = self.engine.analyse(board, engine.Limit(depth=self.depth))
        return {
            "score": stockfish_analysis["score"],
            "move": stockfish_analysis["pv"][0].uci(),
        }

    def get_probability_of_win(self, board: Board, colour_played: str):
        stockfish_analysis = self.engine.analyse(board, engine.Limit(depth=self.depth))
        return self._get_probability(stockfish_analysis, colour_played)

    @staticmethod
    def _get_probability(info: dict, colour_played: str):
        if colour_played == "W":
            score = info["score"].white()
        else:
            score = info["score"].black()

        return score.wdl().wins / 1000 + score.wdl().draws / 2000
