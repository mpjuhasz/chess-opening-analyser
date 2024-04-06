from functools import lru_cache
from chess import Board, engine
from chess_opening_analyser.games import PlayerColour


class Stockfish:
    def __init__(self, stockfish_path: str, analysis_depth=10):
        self.engine = engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = analysis_depth

    @lru_cache(maxsize=2**14)
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
        if board.is_game_over():
            return {
                "score": self._pseudo_probability(
                    board.result(), colour_played=colour_played
                ),
                "best_move": "",
            }
        stockfish_analysis = self.engine.analyse(board, engine.Limit(depth=self.depth))
        assert (
            "score" in stockfish_analysis
        ), "Stockfish analysis did not return a score"
        assert "pv" in stockfish_analysis, "Stockfish analysis did not return a pv"
        return {
            "score": self._get_probability(stockfish_analysis["score"], colour_played),
            "best_move": stockfish_analysis["pv"][0].uci(),
        }

    @staticmethod
    def _pseudo_probability(result: str, colour_played: PlayerColour) -> float:
        if result == "1-0":
            return 1.0 if colour_played == PlayerColour.W else 0.0
        if result == "0-1":
            return 0.0 if colour_played == PlayerColour.W else 1.0
        return 0.5

    @staticmethod
    def _get_probability(info: engine.PovScore, colour_played: PlayerColour) -> float:
        if colour_played == PlayerColour.W:
            score = info.white()
        else:
            score = info.black()

        return score.wdl().wins / 1000 + score.wdl().draws / 2000

    def quit(self):
        self.engine.quit()
