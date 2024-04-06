from typing import Optional
from chess_opening_analyser.openings.opening import Opening
from chess_opening_analyser.openings.tree import Tree
from chess_opening_analyser.engine.stockfish import Stockfish
from chess_opening_analyser.opening_directory import EcoDB
from chess_opening_analyser.games import PlayerColour
from chess_opening_analyser.logger import logger

import io

from itertools import zip_longest
from datetime import datetime
from chess.pgn import Game, read_game, ChildNode


class GameProcessor:
    """Processor to parse and analyse games, adding them to the opening tree"""

    MOVE_DELAY = 5
    FORBIDDEN_VARIANTS = [
        "3-check",
        "Crazyhouse",
        "Chess960",
        "Bughouse",
        "King of the Hill",
    ]

    def __init__(self, tree: Tree, stockfish: Stockfish, eco_db: EcoDB, user: str):
        self.tree = tree
        self.engine = stockfish
        self.user = user
        self.eco_db = eco_db
        # TODO the above ones should be moved out of the processor

    def process_game(self, game_pgn: str) -> None:
        """Processes a single game, adding the openings to the tree"""
        game = self._read_game(game_pgn)

        if game.headers.get("Variant", None) in self.FORBIDDEN_VARIANTS:
            return

        colour = self._get_player_colour(game)

        head = self.tree.root
        game_metadata = self._game_metadata(game)
        empty_moves = 0
        fens = []
        scores = []

        moves = list(game.mainline())

        for move in moves:
            if empty_moves > self.MOVE_DELAY:
                break

            fen = self._fen_parser(move.board().fen())
            fens.append(fen)

            openings_data = self.eco_db.lookup(fen)
            engine_analysis = self.engine.get_best_move(fen, colour)
            scores.append(engine_analysis["score"])

            if openings_data:
                empty_moves = 0
                opening = Opening(**openings_data)

                opening.update_opening(
                    **game_metadata,  #  type: ignore
                    colour=colour,
                    following_move=self._next_move(openings_data["num_moves"], moves),
                    **engine_analysis,  #  type: ignore
                )

                self.tree.add_opening(opening, head=head, player_colour=colour)
                head = opening
            else:
                empty_moves += 1

        self._update_next_move_scores(fens, scores, empty_moves, game_metadata)

    def _get_player_colour(self, game: Game) -> PlayerColour:
        """Gets the colour of the player in the game"""
        return PlayerColour.W if game.headers["White"] == self.user else PlayerColour.B

    def _update_next_move_scores(
        self,
        fens: list[str],
        scores: list[float],
        empty_moves: int,
        game_metadata: dict[str, datetime | float],
    ) -> None:
        """Updates the `score_in_n_moves` attribute of the nodes in the tree using the move delay"""
        fillvalue = game_metadata["result"] if empty_moves <= self.MOVE_DELAY else -1.0
        assert isinstance(fillvalue, float), "The fillvalue should be a float"

        for fen, score_in_n_moves in zip_longest(
            fens, scores[self.MOVE_DELAY - 1 :], fillvalue=fillvalue
        ):
            if fen in self.tree.nodes.keys():
                assert isinstance(fen, str), "The FEN should be a string"
                self.tree.nodes[fen].score_in_n_moves.append(score_in_n_moves)

    @staticmethod
    def _fen_parser(fen: str) -> str:
        """
        Parses the FEN string to remove the move number and the full move count

        Ref https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
        """
        board, turn, castling, en_passant, _, _ = fen.split()
        return f"{board} {turn} {castling} {en_passant}"

    @staticmethod
    def _next_move(move_num: int, moves: list[ChildNode]) -> Optional[str]:
        """Gets the following move on the board"""
        if move_num < len(moves):
            return moves[move_num].uci()
        return None

    @staticmethod
    def _read_game(game_pgn: str) -> Game:
        """Reads a game from a string"""
        game = read_game(io.StringIO(game_pgn))
        assert isinstance(game, Game), "The game could not be read"
        return game

    def _game_metadata(self, game: Game) -> dict[str, datetime | float]:
        """
        Extracts the metadata from the game

        Args:
            game (Game): the game to extract the metadata from

        Returns:
            dict[str, datetime | float]: the metadata in the format of:
            {
                "result": float,
                "date": datetime,
            }
        """
        return {
            "result": self._extract_result(game.headers["Termination"]),
            "date": datetime.strptime(game.headers["Date"], "%Y.%m.%d"),
        }

    def _extract_result(self, termination: str) -> float:
        """Returns the final result of the game being 0 for a loss, 0.5 for a draw and 1 for a win"""
        if self.user + " won" in termination:
            return 1.0
        elif "draw" in termination:
            return 0.5
        else:
            return 0.0
