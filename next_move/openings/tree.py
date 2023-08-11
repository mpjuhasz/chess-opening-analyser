from next_move.openings.opening import Opening
from collections import defaultdict

class Tree:
    def __init__(self):
        self.root = Opening(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
            eco="ROOT"
        )

        self.graph = defaultdict(list)

    def add_opening(self, opening: Opening, head: Opening = None):
        pass
