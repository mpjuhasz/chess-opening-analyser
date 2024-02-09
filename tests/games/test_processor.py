from data_loader import load_game
from next_move.games.processor import GameProcessor


def test_game_processing_results():
    game_str = load_game()

    game_processor = GameProcessor(None, None, None, "matyasj")
    game = game_processor._read_game(game_str)
    metadata = game_processor._game_metadata(game)
    
    assert metadata["result"] == 0.5
    assert metadata["date"].year == 2023
    
