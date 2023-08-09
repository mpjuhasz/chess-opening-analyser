import networkx

from opening import Opening


class Tree:
    def __init__(self):
        self.graph = networkx.DiGraph()
        self.graph.add_node(
            Opening(
                fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -", eco="ROOT"
            )
        )

    def add_opening(self, opening: Opening, head: Opening):
        pass

    @property
    def _root(self):
        pass