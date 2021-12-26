from chess.pgn import Game
from typing import List


def op_id(name: str, moves: int):
    return str(name) + ' - ' + str(moves)


class OpeningNode(object):
    """Opening node for the OpeningGraph. Contains the name, moves children, heads and occurrence of the opening."""
    def __init__(self, name: str, num_moves: int, fen: str, eco: str, result: int):
        self.opening_id = op_id(name, num_moves)
        self.eco = eco
        self.name = name
        self.num_moves = num_moves
        self.occurrence = 1
        self.fen = fen
        self.wins = result
        self.last_moves = dict()
        self.final_pos = ''
        self.later_scores: List[float] = []

    def add_last_move(self, last_move: str):
        if last_move in self.last_moves.keys():
            self.last_moves[last_move] += 1
        else:
            self.last_moves[last_move] = 1

    def add_score(self, score: float):
        self.later_scores.append(score)

    def get_opening_score(self):
        if len(self.later_scores) == 0:
            print('ERROR: zero later scores', self.name)
            return 0.0
        return sum(self.later_scores) / len(self.later_scores)