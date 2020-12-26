import chess.pgn
import requests
import json
import io
import pandas as pd
from flask_restful import Api, Resource
from flask import request, Response, jsonify


archive_url = 'https://api.chess.com/pub/player/'


class User(Resource):
    @staticmethod
    def post():
        print('handling request')
        json = request.get_json(force=True)
        print(json)
        user_name = json['userName']
        print('User received: ', user_name)
        cg = ChessGames(user_name)
        cg.get_all_games()
        print('Number of games: ', len(cg.games))


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
            monthly = [game['pgn'] for game in monthly]
            return monthly
        print('No games...')
        return []

    @staticmethod
    def parse_games(games):
        return [chess.pgn.read_game(io.StringIO(game_pgn)) for game_pgn in games]

    def get_all_games(self):
        archs = self.get_archives()
        req_list = self.game_urls(archs)
        games = []
        for req_url in req_list:
            games += self.get_game(req_url)
        parsed_games = self.parse_games(games)
        self.games = parsed_games