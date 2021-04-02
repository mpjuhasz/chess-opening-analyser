import networkx as nx
from openings_node import OpeningNode

root_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
white_openings_graph = nx.DiGraph()
black_openings_graph = nx.DiGraph()

root_node = OpeningNode('ROOT', 0, root_fen, '000', 0)

white_openings_graph.add_node(root_node)
black_openings_graph.add_node(root_node)

trees = {'W': white_openings_graph, 'B': black_openings_graph}

