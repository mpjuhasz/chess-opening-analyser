from next_move.engine.stockfish import Stockfish
from next_move.games.chess_com import ChessCom
from next_move.openings.tree import Tree
from next_move.games.processor import GameProcessor
from next_move.opening_directory import EcoDB

# from next_move.visualiser.visualiser import Visualiser

from tqdm import tqdm
from typing import Optional

import click


def run_analysis(player_id: str) -> Tree:
    tree = Tree()
    chess_com = ChessCom()
    # visualiser = Visualiser()
    games = chess_com.get_all_games(player_id)
    stockfish = Stockfish("16/bin/stockfish")
    eco_db = EcoDB("eco/openings.json")

    game_processor = GameProcessor(tree, stockfish, eco_db, player_id)

    for game in tqdm(games):
        game_processor.process_game(game)

    stockfish.quit()  # it's fine for now, but will need to refactor this into a context manager

    # visualiser.sankey(
    #     **game_processor.tree.to_sankey(prune_below_count=5), path="tree.html"
    # )
    # visualiser.timeline(
    #     game_processor.tree.to_timeline(breakdown="M"), path="timeline.png"
    # )

    # df = tree.to_opening_strength()
    # df.to_csv("opening_strength.csv")

    tree.to_json(f"next_move/cache/trees/{player_id}.json")

    return tree


@click.command()
@click.option("--player-id", required=True, help="The player id to analyse")
def create_tree(player_id: str, months: Optional[list[str]] = None) -> Tree:
    return run_analysis(player_id)


if __name__ == "__main__":
    create_tree()
