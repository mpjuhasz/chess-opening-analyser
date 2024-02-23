from next_move.openings.tree import Tree
from next_move.openings.opening import Opening


def test_tree():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
        num_moves=1,
    )

    tree.add_opening(first_opening, head=tree.root)
    # TODO needs updating
    # assert tree.graph[tree.root][first_opening] == 1
    # assert list(tree.graph.keys()) == [tree.root]
    # assert tree.graph[tree.root].most_common() == [(first_opening, 1)]


def test_most_common_child():
    tree = Tree()
    first_opening = Opening(
        fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        eco="King's pawn",
        name="King's pawn",
        num_moves=1,
    )

    tree.add_opening(first_opening, head=tree.root)
    # TODO needs updating
    # assert tree.most_common_child(tree.root, 1) == [(first_opening, 1)]
