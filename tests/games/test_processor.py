from data_loader import load_game
from next_move.games.processor import GameProcessor
from next_move.openings.tree import Tree
from next_move.engine.stockfish import Stockfish
from next_move.opening_directory import EcoDB


def test_game_processing_results():
    game_str = load_game()

    game_processor = GameProcessor(None, None, None, "matyasj")
    game = game_processor._read_game(game_str)
    metadata = game_processor._game_metadata(game)
    
    assert metadata["result"] == 0.5
    assert metadata["date"].year == 2023
    
def test_game_processing():
    game_str = load_game()
    tree = Tree()
    stockfish = Stockfish("16/bin/stockfish")
    eco_db = EcoDB("eco/openings.json")
    
    game_processor = GameProcessor(tree, stockfish, eco_db, "matyasj")
    
    game_processor.process_game(game_str)
    
    print(tree)
    
    # TODO need to identify how to test the tree
    
    