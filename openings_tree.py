from typing import List, Tuple
from stockfish_hook import stockfish_best_move


def op_id(name: str, moves: int):
    return str(name) + ' - ' + str(moves)


class NMOpening(object):
    """
    Opening object for the OpeningTree. Contains the name, moves children, heads and occurrence of the opening.
    """
    def __init__(self, name, moves):
        self.opening_id = op_id(name, moves)
        self.name = name
        self.moves = moves
        self.children = dict()
        self.heads = dict()
        self.occurrence = 1
        self.wins = 0
        self.last_moves = dict()
        self.final_pos = ''
        self.ucis = []
        self.date = ''
        self.later_scores = dict()

    def add_child(self, child_tuple: Tuple[str, int]):
        child = op_id(child_tuple[0], child_tuple[1])
        if child in self.children.keys():
            self.children[child] += 1
        else:
            self.children[child] = 1

    def add_head(self, head_tuple: Tuple[str, int]):
        head = op_id(head_tuple[0], head_tuple[1])
        if head in self.heads.keys():
            self.heads[head] += 1
        else:
            self.heads[head] = 1

    def add_last_move(self, last_move: str):
        if last_move in self.last_moves.keys():
            self.last_moves[last_move] += 1
        else:
            self.last_moves[last_move] = 1


class NMOpeningTree(object):
    """
    The opening tree contains the user's openings, it consists of NMOpening objects. It is a tree structure, where each
    opening can have children and heads (meaning the openings the user proceeded to and the ones succeeding this
    position).
    """
    def __init__(self, colour: str):
        self.openings: List[NMOpening] = []
        self.colour = colour
        self.total_openings = 0

    def get_opening(self, name: str, move: int) -> List[NMOpening]:
        """
        Gets the opening. Each opening must be unique for the tuple: (Name, Moves)
        """
        ops = [op for op in self.openings if op.opening_id == op_id(name, move)]
        if len(ops) > 1:
            print('Error in tree: opening present multiple times.', ops)
        return ops

    def add_opening(self, name: str, move: int, result=0, last_move='', child=(), head=(),
                    final_pos='', uci='', date='', later_fens=[]):
        """
        Adds a new opening, or updates an existing one. Updates the occurrence and the children and heads.
        """
        ops = self.get_opening(name, move)
        self.total_openings += 1
        if ops:
            ops[0].occurrence += 1
            new_op = ops[0]
        else:
            new_op = NMOpening(name, move)
            new_op.final_pos = final_pos
            self.openings.append(new_op)

        colour = 'WHITE' if self.colour == 'W' else 'BLACK'

        for idx in range(0, 4):
            if idx < len(later_fens):
                best_move = stockfish_best_move(later_fens[idx])
                if idx in new_op.later_scores.keys():
                    new_op.later_scores[idx].append(best_move[0].pov(colour).score(mate_score=1000))
                else:
                    new_op.later_scores[idx] = [best_move[0].pov(colour).score(mate_score=1000)]

        new_op.date = date
        new_op.wins += result
        if child:
            new_op.add_child(child)
        if head:
            new_op.add_head(head)
        if last_move:
            new_op.add_last_move(last_move)
        if uci and uci not in new_op.ucis and len(uci.split(' ')) == move:
            new_op.ucis.append(uci)

    def ops_by_move(self, move: int):
        return [op for op in self.openings if op.moves == move]

    def ops_by_name(self, name: str):
        return [op for op in self.openings if op.name == name]

    def get_top_openings(self):
        rem = 0 if self.colour == 'W' else 1
        finals = [op for op in self.openings if op.last_moves and op.moves % 2 == rem]
        finals.sort(key=lambda x: sum(x.following_moves.values()), reverse=True)
        return finals[:5]

    def get_worst_openings(self, limit_ratio):
        rem = 0 if self.colour == 'W' else 1
        finals = [op for op in self.openings if op.last_moves and op.moves % 2 == rem
                  and op.occurrence > self.total_openings / 200 and op.wins / op.occurrence < limit_ratio]
        finals.sort(key=lambda x: x.wins / x.occurrence, reverse=False)
        return finals[:5]

    def get_best_scoring(self, move):
        finals = [(op, sum(op.later_scores[move])/len(op.later_scores[move])) for op in self.openings
                  if move in op.later_scores.keys()]
        finals.sort(key=lambda x: x[1], reverse=False)
        return [op[0] for op in finals[:5]]


class NMGameOpenings(object):
    def __init__(self, openings: List[Tuple[str, int]], last_move: str, opening_end_pos: str, colour_played: str,
                 result: int, uci: str, date: str, later_fens: list):
        self.openings = openings
        self.last_move = last_move
        self.opening_end_pos = opening_end_pos
        self.colour_played = colour_played
        self.result = result
        self.uci = uci
        self.date = date
        self.later_fens = later_fens

    def load_into_tree(self, tree: NMOpeningTree):
        total_openings = len(self.openings)
        for op_idx, op in enumerate(self.openings):
            name = op[0]
            moves = op[1]
            head = self.openings[op_idx-1] if op_idx-1 != -1 else ()
            child = self.openings[op_idx+1] if op_idx+1 < total_openings else ()
            last_move = self.last_move if op_idx+1 == total_openings else ''
            tree.add_opening(name, moves, self.result, last_move, child, head, self.opening_end_pos, self.uci,
                             self.date, self.later_fens)
