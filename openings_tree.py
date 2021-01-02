from typing import List, Tuple


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
        self.final_pos = ''
        self.ucis = []

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

    def add_opening(self, name: str, move: int, result=0, last_move='', child=(), head=(), final_pos='', uci=''):
        """
        Adds a new opening, or updates an existing one. Updates the occurrence and the children and heads.
        """
        ops = self.get_opening(name, move)
        if ops:
            ops[0].occurrence += 1
            new_op = ops[0]
        else:
            new_op = NMOpening(name, move)
            new_op.final_pos = final_pos
            self.openings.append(new_op)

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
        finals.sort(key=lambda x: sum(x.last_moves.values()), reverse=True)
        return finals[:5]


class NMGameOpenings(object):
    def __init__(self, openings: List[Tuple[str, int]], last_move: str, opening_end_pos: str, colour_played: str,
                 result: int, uci: str):
        self.openings = openings
        self.last_move = last_move
        self.opening_end_pos = opening_end_pos
        self.colour_played = colour_played
        self.result = result
        self.uci = uci

    def load_into_tree(self, tree: NMOpeningTree):
        total_openings = len(self.openings)
        for op_idx, op in enumerate(self.openings):
            name = op[0]
            moves = op[1]
            head = self.openings[op_idx-1] if op_idx-1 != -1 else ()
            child = self.openings[op_idx+1] if op_idx+1 < total_openings else ()
            last_move = self.last_move if op_idx+1 == total_openings else ''
            tree.add_opening(name, moves, self.result, last_move, child, head, self.opening_end_pos, self.uci)
