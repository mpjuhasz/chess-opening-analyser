from chess import Board, engine
from pathlib import Path


class Stockfish:
    def __init__(self, stockfish_path: str | Path, analysis_depth=10):
        self.engine = engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = analysis_depth

    def get_best_move(self, fen: str) -> dict[str, float | str]:
        """
        Gets the best next move for the given fen

        Args:
            fen (str): FEN of the board

        Returns:
            dict: {"score": chess.engine.Score, "best_move": str}: the best next move and corresponding score
        """
        board = Board(fen=fen)
        stockfish_analysis = self.engine.analyse(board, engine.Limit(depth=self.depth))
        return {
            "score": stockfish_analysis["score"],
            "best_move": stockfish_analysis["pv"][0].uci(),
        }  # TODO this should return probability of winning, right now it's a PovScore

    def get_probability_of_win(self, board: Board, colour_played: str) -> float:
        """Gets the probability of winning for the coulour_played in the given board"""
        stockfish_analysis = self.engine.analyse(board, engine.Limit(depth=self.depth))
        return self._get_probability(stockfish_analysis, colour_played)

    @staticmethod
    def _get_probability(info: dict, colour_played: str) -> float:
        if colour_played == "W":
            score = info["score"].white()
        else:
            score = info["score"].black()

        return score.wdl().wins / 1000 + score.wdl().draws / 2000
