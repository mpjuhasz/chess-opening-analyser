from chess_opening_analyser.engine.stockfish import Stockfish
from chess_opening_analyser.games.chess_com import ChessCom
from chess_opening_analyser.openings.tree import Tree
from chess_opening_analyser.games.processor import GameProcessor
from chess_opening_analyser.opening_directory import EcoDB

# from next_move.visualiser.visualiser import Visualiser

from pathlib import Path
from tqdm import tqdm
from typing import Optional

from dotenv import load_dotenv, find_dotenv

import click
import os


load_dotenv(find_dotenv())


def run_analysis(player_id: str) -> Tree:
    if Path(f"chess_opening_analyser/cache/trees/{player_id}.json").exists():
        return Tree.from_json(f"chess_opening_analyser/cache/trees/{player_id}.json")
    else:
        tree = Tree()
        chess_com = ChessCom()

        games = chess_com.get_all_games(player_id)
        stockfish = Stockfish(os.environ["STOCKFISH_DIR"])
        eco_db = EcoDB("eco/openings.json")

        game_processor = GameProcessor(tree, stockfish, eco_db, player_id)

        for game in tqdm(games):
            game_processor.process_game(game)

        stockfish.quit()  # it's fine for now, but will need to refactor this into a context manager

        tree.to_json(f"chess_opening_analyser/cache/trees/{player_id}.json")

        return tree


@click.command()
@click.option("--player-id", required=True, help="The player id to analyse")
def create_tree(player_id: str, months: Optional[list[str]] = None) -> Tree:
    return run_analysis(player_id)


if __name__ == "__main__":
    create_tree()
