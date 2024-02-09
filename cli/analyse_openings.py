from next_move.engine.stockfish import Stockfish
from next_move.games.chess_com import ChessCom
from next_move.openings.tree import Tree
from next_move.games.processor import GameProcessor
from next_move.opening_directory import EcoDB

import click

@click.command()
@click.option("--player-id", required=True, help="The player id to analyse")
def create_tree(player_id: str, months: list[str] = None) -> Tree:
    tree = Tree()
    chess_com = ChessCom()
    games = chess_com.get_all_games(player_id)
    stockfish = Stockfish("16/bin/stockfish")
    eco_db = EcoDB("eco/openings.json")

    game_processor = GameProcessor(tree, stockfish, eco_db, player_id)
    
    for game in games[:10]:
        game_processor.process_game(game)

    print(game_processor.tree)
    return


if __name__ == "__main__":
    create_tree()
