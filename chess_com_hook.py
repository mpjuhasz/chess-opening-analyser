import chess.pgn
import requests
import json
import io
import os
from flask_restful import Resource
from flask import request
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


CACHE_DIR = Path('./cache')
ARCHIVE_URL = 'https://api.chess.com/pub/player/'
GAMES_EXT = '/games/archives'


class ChessGames(object):
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.games = []

    def get_archives(self) -> dict:
        games = requests.get(ARCHIVE_URL + self.user_name + GAMES_EXT)
        return games.json()

    @staticmethod
    def get_game(url: str) -> list[str]:
        monthly_archive = requests.get(url).json()
        return [game.get("pgn", "") for game in monthly_archive.get("games", [])]

    def load_from_cache(self) -> list[str]:
        with open(Path(CACHE_DIR / f"{self.user_name}.txt"), 'r', encoding='utf-8') as f:
            games = json.load(f)
        return games

    def cache_games(self, games: list[str]):
        with open(Path(CACHE_DIR / f"{self.user_name}.txt"), 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=4)

    def get_all_games(self, only_last_month: bool):
        if os.path.exists(CACHE_DIR / f"{self.user_name}.txt"):
            games = self.load_from_cache()
        else:
            archives = self.get_archives()
            req_list = archives.get("archives", [])
            games = []
            if only_last_month:
                req_list = req_list[-1:]
            for req_url in tqdm(req_list):
                games += self.get_game(req_url)
            self.cache_games(games)
        parsed_games = [chess.pgn.read_game(io.StringIO(game_pgn)) for game_pgn in games]
        self.games = parsed_games


cg = ChessGames('')


class User(Resource):
    @staticmethod
    def post():
        print('handling request')
        json = request.get_json(force=True)
        print(json)
        user_name = json['userName']
        last_month = json.get('onlyLastMonth', False)
        print('User received: ', user_name)
        start_time = datetime.now()
        cg.user_name = user_name
        cg.get_all_games(last_month)
        print('Got games in: ', datetime.now() - start_time)
        print('Number of games: ', len(cg.games))


if __name__ == "__main__":
    start_time = datetime.now()
    cg = ChessGames("matyasj")
    cg.get_all_games(only_last_month=False)
    print(f"Got games in {datetime.now() - start_time}")
    print(f"Got {len(cg.games)} games")
