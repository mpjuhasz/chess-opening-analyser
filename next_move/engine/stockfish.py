from chess import Board, engine
from pathlib import Path
from next_move.games import PlayerColour


class Stockfish:
    def __init__(self, stockfish_path: str | Path, analysis_depth=10):
        self.engine = engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = analysis_depth

    def get_best_move(
        self, fen: str, colour_played: PlayerColour
    ) -> dict[str, float | str]:
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
            "score": self._get_probability(stockfish_analysis["score"], colour_played),
            "best_move": stockfish_analysis["pv"][0].uci(),
        }

    @staticmethod
    def _get_probability(info: dict, colour_played: PlayerColour) -> float:
        if colour_played == PlayerColour.W:
            score = info.white()
        else:
            score = info.black()

        return score.wdl().wins / 1000 + score.wdl().draws / 2000
