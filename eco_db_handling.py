import pandas as pd
from pandas import DataFrame
from typing import Tuple
from chess.pgn import Game
from chess_com_hook import ChessGames
from flask_restful import Resource
from tqdm import trange
# from openings_tree import NMOpening, NMOpeningTree, NMGameOpenings
# from stockfish_hook import stockfish_best_move


def build_eco_db() -> DataFrame:
    openings = pd.read_json('./eco/openings.json')
    print('Loaded eco data:', len(openings))
    return openings


eco_db = build_eco_db()


def eco_lookup(fen: str) -> Tuple[str, str, str, int]:
    """Looks up the fen in the database, and returns the ECO, name, moves and number of moves"""
    ind = list(eco_db['fen']).index(fen)
    name = eco_db.loc[ind]['name']
    eco = eco_db.loc[ind]['eco']
    num_moves =  len(eco_db.loc[ind]['moves'].split(' '))
    moves = eco_db.loc[ind]['moves']
    return eco, name, moves, num_moves