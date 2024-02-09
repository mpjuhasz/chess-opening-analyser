from next_move.openings.opening import Opening
from next_move.openings.tree import Tree
from next_move.engine.stockfish import Stockfish
from next_move.opening_directory import EcoDB
from next_move.games import PlayerColour

import io

from datetime import datetime
from chess.pgn import Game, read_game


class GameProcessor:
    """Processor to parse and analyse games, adding them to the opening tree"""
    def __init__(self, tree: Tree, stockfish: Stockfish, eco_db: EcoDB, user: str):
        self.tree = tree
        self.engine = stockfish
        self.user = user
        self.eco_db = eco_db
        # TODO the above ones should be moved out of the processor

    def process_game(self, game_pgn: str) -> None:
        """Processes a single game, adding the openings to the tree"""
        game = self._read_game(game_pgn)
        
        colour = self._get_player_colour(game)
        
        head = self.tree.root
        game_metadata = self._game_metadata(game)
        empty_moves = 0

        for move in game.mainline():
            if empty_moves > 5:
                break
    
            fen = self._fen_parser(move.board().fen())
            
            openings_data = self.eco_db.lookup(fen)

            if openings_data:
                opening = Opening(**openings_data)

                opening.update_opening(
                    **game_metadata,
                    following_move=move.uci(),
                    **self.engine.get_best_move(fen, colour)
                )
                
                self.tree.add_opening(opening, head=head)
                head = opening
            else:
                empty_moves += 1

    def _get_player_colour(self, game: Game) -> PlayerColour:
        """Gets the colour of the player in the game"""
        return PlayerColour.W if game.headers['White'] == self.user else PlayerColour.B

    @staticmethod
    def _fen_parser(fen: str) -> str:
        """
        Parses the FEN string to remove the move number and the full move count
        
        Ref https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
        """
        board, turn, castling, en_passant, _, _ = fen.split()
        return f"{board} {turn} {castling} {en_passant}"

    @staticmethod
    def _read_game(game_pgn: str) -> Game:
        """Reads a game from a string"""
        return read_game(io.StringIO(game_pgn))

    def _game_metadata(self, game: Game) -> dict:
        """
        Extracts the metadata from the game
        
        Args:
            game (Game): the game to extract the metadata from
            
        Returns:
            dict[str, float | str]: the metadata in the format of:
            {
                "result": float,
                "date": datetime,
            }
        """
        return {
            "result": self._extract_result(game.headers['Termination']),
            "date": datetime.strptime(game.headers['Date'], "%Y.%m.%d"),
        }

    def _extract_result(self, termination: str) -> float:
        """Returns the final result of the game being 0 for a loss, 0.5 for a draw and 1 for a win"""
        return 1.0 if self.user + " won" in termination else 0.5 if "draw" in termination else 0.0
