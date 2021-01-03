from chess_com_hook import cg
import pandas as pd
from pandas import DataFrame
from chess.pgn import Game
from chess_com_hook import ChessGames
from flask_restful import Resource
from tqdm import trange
from openings_tree import NMOpening, NMOpeningTree, NMGameOpenings
from stockfish_hook import stockfish_best_move

def print_tree_debug(tree: NMOpeningTree, type='top', limit_ratio=1):
    print('------------------------------------------')
    ops = []
    if type == 'top':
        ops = tree.get_top_openings()
    elif type == 'worst':
        ops = tree.get_worst_openings(limit_ratio)

    colour = 'WHITE' if tree.colour == 'W' else 'BLACK'

    print('TYPE: ', type.upper())
    for tup in [(to.opening_id, to.moves, to.occurrence, to.wins, to.last_moves, to.children, to.final_pos, to.ucis)
                for to in ops]:
        print(tup[0])
        print(' - moves: ', tup[7], '(', tup[1], ')')
        print(' - wins: ', tup[3], '/', tup[2])
        print(' - last moves: ', tup[4])
        best_move = stockfish_best_move(tup[6])
        print(' - best move is: ', best_move[1], '(score: ', best_move[0].pov(colour).score(mate_score=1000), ')')
        print(' - changed into: ', tup[5])


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
        nmo = NMGameOpenings([], '', '', colour_played, result, '', game.headers['Date'])
        total_moves = len(list(game.mainline()))
        extra_moves = 0
        while extra_moves < 4 or not end_of_opening:
            end_of_opening = True
            if move < total_moves:
                fen = list(game.mainline())[move].board().fen().split('-')[0] + '-'
                if extra_moves == 0:
                    nmo.last_move = list(game.mainline())[move].uci()
                if fen in list(self.eco_db['fen']):
                    ind = list(self.eco_db['fen']).index(fen)
                    end_of_opening = False
                    nmo.openings.append((self.eco_db.loc[ind]['name'], len(self.eco_db.loc[ind]['moves'].split(' '))))
                    nmo.uci = self.eco_db.loc[ind]['moves']
                    nmo.opening_end_pos = fen
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
        # for i in range(0, 5):
        #     most_black = max(self.tree_black.ops_by_move(i+1), key=lambda x: x.occurrence)
        #     most_white = max(self.tree_white.ops_by_move(i+1), key=lambda x: x.occurrence)
        #     print('black: ', most_black.name, most_black.moves, most_black.occurrence)
        #     print('white: ', most_white.name, most_white.moves, most_white.occurrence)
        print_tree_debug(self.tree_white, type='top')
        print_tree_debug(self.tree_black, type='top')
        print_tree_debug(self.tree_white, type='worst', limit_ratio=0.45)
        print_tree_debug(self.tree_black, type='worst', limit_ratio=0.45)
        # print(game_nmo.openings)
        # print(game_nmo.last_move)
        # print(game_nmo.opening_end_pos)
        # print(game_nmo.colour_played)


otb = OpeningsTreeBuilder()


class OTB(Resource):
    @staticmethod
    def get():
        print('handling request')
        otb(cg)
