from next_move.openings.tree import Tree
from next_move.openings.opening import Opening


def test_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn"
    )
    tree.add_opening(first_opening)
    assert tree.graph[tree.root][first_opening]['weight'] == 1
