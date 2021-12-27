import chess.pgn
import requests
import json
import io
import os
import pandas as pd
from flask_restful import Api, Resource
from flask import request, Response, jsonify
from datetime import datetime


cache_dir = './cache/'
archive_url = 'https://api.chess.com/pub/player/'


class ChessGames(object):
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.games = []

    def get_archives(self) -> dict:
        games = requests.get(archive_url + self.user_name + '/games/archives')
        return games.json()

    @staticmethod
    def game_urls(archives: dict) -> list:
        if 'archives' in archives.keys():
            req_list = archives['archives']
            return req_list
        return []

    @staticmethod
    def get_game(url: str) -> list:
        monthly = requests.get(url)
        if 'games' in monthly.json().keys():
            monthly = monthly.json()['games']
            monthly = [game['pgn'] for game in monthly if 'pgn' in game.keys()]  # This shouldn't really be the case
            return monthly
        print('No games...')
        return []

    @staticmethod
    def parse_games(games):
        return [chess.pgn.read_game(io.StringIO(game_pgn)) for game_pgn in games]

    def get_all_games(self, only_last_month: bool):
        if not os.path.exists(cache_dir + self.user_name + '.txt'):
            archs = self.get_archives()
            req_list = self.game_urls(archs)
            games = []
            if only_last_month:
                # print(req_list)
                req_list = req_list[-1:]
                # print(req_list)
            for req_url in req_list:
                games += self.get_game(req_url)
            with open(cache_dir + self.user_name + '.txt', 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)
        else:
            print('cached stuff...')
            with open(cache_dir + self.user_name + '.txt', 'r', encoding='utf-8') as f:
                games = json.load(f)
        parsed_games = self.parse_games(games)
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
