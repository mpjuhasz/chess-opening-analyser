from chess_com_hook import cg
import pandas as pd
from pandas import DataFrame
import chess
from chess.pgn import Game
from chess_com_hook import ChessGames
from typing import List, Tuple
from flask_restful import Api, Resource
from flask import request, Response, jsonify
from tqdm import tqdm, trange


class NMOpening(object):
    """
    Opening object for the OpeningTree. Contains the name, moves children, heads and occurrence of the opening.
    """
    def __init__(self, name, moves):
        self.name = name
        self.moves = moves
        self.children = dict()
        self.heads = dict()
        self.occurrence = 1
        self.wins = 0
        self.last_moves = dict()

    def add_child(self, child_tuple: Tuple[str, int]):
        if child_tuple in self.children.keys():
            self.children[child_tuple] += 1
        else:
            self.children[child_tuple] = 1

    def add_head(self, head_tuple: Tuple[str, int]):
        if head_tuple in self.heads.keys():
            self.heads[head_tuple] += 1
        else:
            self.heads[head_tuple] = 1

    def add_last_move(self, last_move: str):
        if last_move in self.last_moves.keys():
            self.last_moves[last_move] += 1
        else:
            self.last_moves[last_move] = 1

    def get_tuple(self):
        return self.name, self.moves


class NMOpeningTree(object):
    """
    The opening tree contains the user's openings, it consists of NMOpening objects. It is a tree structure, where each
    opening can have children and heads (meaning the openings the user proceeded to and the ones succeeding this
    position).
    """
    def __init__(self, colour: str):
        self.openings: List[NMOpening] = []
        self.colour = colour

    def get_opening(self, name: str, move: int) -> List[NMOpening]:
        """
        Gets the opening. Each opening must be unique for the tuple: (Name, Moves)
        """
        ops = [op for op in self.openings if op.name == name and op.moves == move]
        if len(ops) > 1:
            print('Error in tree: opening present multiple times.', ops)
        return ops

    def add_opening(self, name: str, move: int, result=0, last_move='', child=(), head=()):
        """
        Adds a new opening, or updates an existing one. Updates the occurrence and the children and heads.
        """
        ops = self.get_opening(name, move)
        if ops:
            ops[0].occurrence += 1
            new_op = ops[0]
        else:
            new_op = NMOpening(name, move)
            self.openings.append(new_op)

        new_op.wins += result
        if child:
            new_op.add_child(child)
        if head:
            new_op.add_head(head)
        if last_move:
            new_op.add_last_move(last_move)

    def ops_by_move(self, move: int):
        return [op for op in self.openings if op.moves == move]

    def ops_by_name(self, name: str):
        return [op for op in self.openings if op.name == name]

    def get_top_openings(self):
        finals = [op for op in self.openings if op.last_moves]
        finals.sort(key=lambda x: sum(x.last_moves.values()), reverse=True)
        return finals[:5]

class NMGameOpenings(object):
    def __init__(self, openings: List[Tuple[str, int]], last_move: str, opening_end_pos: str, colour_played: str,
                 result: int):
        self.openings = openings
        self.last_move = last_move
        self.opening_end_pos = opening_end_pos
        self.colour_played = colour_played
        self.result = result

    def load_into_tree(self, tree: NMOpeningTree):
        total_openings = len(self.openings)
        for op_idx, op in enumerate(self.openings):
            name = op[0]
            moves = op[1]
            head = self.openings[op_idx-1] if op_idx-1 != -1 else ()
            child = self.openings[op_idx+1] if op_idx+1 < total_openings else ()
            last_move = self.last_move if op_idx+1 == total_openings else ''
            tree.add_opening(name, moves, self.result, last_move, child, head)


class OpeningsTreeBuilder(object):
    """
    Builds the OpeningsTree of the user's games. This is using the ECO database, to match the openings to the game.
    """
    def __init__(self):
        self.eco_db = self.build_eco_db()
        self.tree_white = NMOpeningTree('W')
        self.tree_black = NMOpeningTree('B')
        self.nmo_list = []

    @staticmethod
    def build_eco_db() -> DataFrame:
        openings = pd.read_json('./eco/openings.json')
        print('Loaded eco data:', len(openings))
        return openings

    def parse_game_into_nmopening(self, game: Game, user_name: str) -> NMGameOpenings:
        """
        Parses the game into an NMGameOpenings object.
        :param game: the parsed game from chess_com_hook
        :param user_name: user name
        :return: NMGameOpenings object
        """
        colour_played = 'W' if game.headers['White'] == user_name else 'B'
        move = 0
        end_of_opening = False
        result = 1 if user_name + ' won' in game.headers['Termination'] else 0
        nmo = NMGameOpenings([], '', '', colour_played, result)
        total_moves = len(list(game.mainline()))
        extra_moves = 0
        while extra_moves < 4 or not end_of_opening:
            end_of_opening = True
            if move < total_moves:
                fen = list(game.mainline())[move].board().fen().split('-')[0] + '-'
                if extra_moves == 0:
                    nmo.last_move = list(game.mainline())[move].uci()
                    nmo.opening_end_pos = fen
                if fen in list(self.eco_db['fen']):
                    ind = list(self.eco_db['fen']).index(fen)
                    end_of_opening = False
                    nmo.openings.append((self.eco_db.loc[ind]['name'], len(self.eco_db.loc[ind]['moves'].split(' '))))
                    if extra_moves > 1:
                        print(nmo.openings[-1][0], '... from ...', nmo.openings[-2][0])
                    extra_moves = 0
                else:
                    extra_moves += 1
            else:
                extra_moves += 1
            move += 1
        return nmo

    def __call__(self, cg_processed: ChessGames):
        """
        A call to the OTB creates the NMGameOpenings objects for each game
        :param cg_processed: ChessGames object. Contains the parsed games of a user.
        :return: void
        """
        games = cg_processed.games
        user_name = cg_processed.user_name
        for game_id in trange(len(games)):
            game = games[game_id]
            game_nmo = self.parse_game_into_nmopening(game, user_name)
            if game_nmo.openings:
                # print(game_nmo.openings[-1])
                self.nmo_list.append(game_nmo)
                if game_nmo.colour_played == 'W':
                    game_nmo.load_into_tree(self.tree_white)
                else:
                    game_nmo.load_into_tree(self.tree_black)
        for i in range(0, 5):
            most_black = max(self.tree_black.ops_by_move(i+1), key=lambda x: x.occurrence)
            most_white = max(self.tree_white.ops_by_move(i+1), key=lambda x: x.occurrence)
            print('black: ', most_black.name, most_black.moves, most_black.occurrence)
            print('white: ', most_white.name, most_white.moves, most_white.occurrence)
        print('------------------------------------------')
        for tup in [(to.name, to.moves, to.occurrence, to.wins, to.last_moves, to.children) for to in
                    self.tree_white.get_top_openings()]:
            print(tup[0])
            print(' - moves: ', tup[1])
            print(' - wins: ', tup[3], '/', tup[2])
            print(' - last moves: ', tup[4])
            children = [tc for tc in tup[5]]
            print(' - changed into: ', children)
        print('------------------------------------------')
        for tup in [(to.name, to.moves, to.occurrence, to.wins, to.last_moves, to.children) for to in
                    self.tree_black.get_top_openings()]:
            print(tup[0])
            print(' - moves: ', tup[1])
            print(' - wins: ', tup[3], '/', tup[2])
            print(' - last moves: ', tup[4])
            children = [tc for tc in tup[5]]
            print(' - changed into: ', children)
        print(game_nmo.openings)
        print(game_nmo.last_move)
        print(game_nmo.opening_end_pos)
        print(game_nmo.colour_played)


otb = OpeningsTreeBuilder()


class OTB(Resource):
    @staticmethod
    def get():
        print('handling request')
        otb(cg)

