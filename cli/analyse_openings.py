from functools import reduce
from multiprocessing import Pool
from chess_opening_analyser.engine.stockfish import Stockfish
from chess_opening_analyser.games.chess_com import ChessCom
from chess_opening_analyser.openings.tree import Tree
from chess_opening_analyser.games.processor import GameProcessor
from chess_opening_analyser.opening_directory import EcoDB

from tqdm import tqdm
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from multiprocessing import Pool

import click
import os


load_dotenv(find_dotenv())


def process_games_slice(games_slice, player_id, stockfish_dir, eco_db_path):
    tree = Tree()
    stockfish = Stockfish(stockfish_dir)
    eco_db = EcoDB(eco_db_path)
    game_processor = GameProcessor(tree, stockfish, eco_db, player_id)

    for game in tqdm(games_slice):
        game_processor.process_game(game)

    stockfish.quit()

    return game_processor.tree


def run_analysis(player_id: str, num_workers: int, limit: Optional[int] = None):
    chess_com = ChessCom()
    games = chess_com.get_all_games(player_id)
    stockfish_dir = os.environ["STOCKFISH_DIR"]
    eco_db_path = "eco/openings.json"

    if limit is not None:
        games = games[:limit]

    games_chunks = [games[i::num_workers] for i in range(num_workers)]

    with Pool(processes=num_workers) as pool:
        process_args = [
            (games_chunk, player_id, stockfish_dir, eco_db_path)
            for games_chunk in games_chunks
        ]

        trees = pool.starmap(process_games_slice, process_args)

    tree = reduce(lambda x, y: x + y, trees)
    tree.to_json(f"chess_opening_analyser/cache/trees/{player_id}.json")

    return tree


@click.command()
@click.option("--player-id", required=True, help="Player id to analyse")
@click.option(
    "--num-workers",
    default=8,
    help="Number of workers for parallel processing",
    type=int,
)
@click.option("--limit", default=None, help="Number of games to process", type=int)
def create_tree(player_id: str, num_workers: int, limit: Optional[int]) -> Tree:
    return run_analysis(player_id, num_workers=num_workers, limit=limit)


if __name__ == "__main__":
    create_tree()
