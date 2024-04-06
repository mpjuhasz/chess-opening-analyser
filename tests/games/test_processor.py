from .data_loader import load_game
from chess_opening_analyser.games.processor import GameProcessor
from chess_opening_analyser.openings.tree import Tree
from chess_opening_analyser.engine.stockfish import Stockfish
from chess_opening_analyser.opening_directory import EcoDB

from unittest.mock import MagicMock
from datetime import datetime


def test_game_processing_results(mocker):
    game_str = load_game()

    stockfish = MagicMock(spec=Stockfish)
    eco_db = MagicMock(spec=EcoDB)

    game_processor = GameProcessor(Tree(), stockfish, eco_db, "matyasj")
    game = game_processor._read_game(game_str)
    metadata = game_processor._game_metadata(game)

    assert isinstance(metadata["date"], datetime)
    assert metadata["result"] == 0.5
    assert metadata["date"].year == 2023
