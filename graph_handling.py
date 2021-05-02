from openings_graph import trees, root_fen
from openings_node import OpeningNode
from chess.pgn import Game
from typing import Optional, Dict, List
import networkx as nx
from eco_db_handling import eco_lookup, eco_db
from flask_restful import Resource
from tqdm import trange
from chess_com_hook import cg, ChessGames
from datetime import datetime
import json


# ----------------------------------------------------------------------------------------------------------------------
# NODE HANDLING


def node_by_fen(fen: str, graph: nx.DiGraph) -> Optional[OpeningNode]:
    """Gets the node from the graph with the corresponding fen"""
    nodes = [nd for nd in graph.nodes if nd.fen == fen]
    if nodes:
        return nodes[0]
    return None


def get_opening_node(game: Game, move: int, user_name: str, graph: nx.DiGraph) -> Optional[OpeningNode]:
    """For a move in a game creates the OpeningNode if it doesn't exits yet. Otherwise passes."""
    fen = list(game.mainline())[move].board().fen().split('-')[0] + '-'
    if fen in list(eco_db['fen']):
        result = 1 if user_name + ' won' in game.headers['Termination'] else 0
        node = node_by_fen(fen, graph)
        if node is not None:
            node.occurrence += 1
            node.wins += result
            # node.add_last_move(last_move)
        else:
            eco, name, moves, num_moves = eco_lookup(fen)
            node = OpeningNode(name, num_moves, fen, eco, result)
        return node
    return None


# ----------------------------------------------------------------------------------------------------------------------
# EDGE HANDLING

def handle_edging(source_node: OpeningNode, target_node: OpeningNode, graph: nx.DiGraph):
    """Adds an edge, if there isn't one, otherwise increases the edge weight"""
    if graph.has_successor(source_node, target_node):
        graph[source_node][target_node]['weight'] += 1
    else:
        graph.add_edge(source_node, target_node, weight=1)


# ----------------------------------------------------------------------------------------------------------------------
# GRAPH HANDLING

def add_game_to_graph(trees: Dict[str, nx.DiGraph], game: Game, user_name: str):
    """Takes a Game object and adds it to the OpeningsGraph creating all necessary nodes and linking that's required"""
    colour_played = 'W' if game.headers['White'] == user_name else 'B'
    graph = trees[colour_played]
    total_moves = len(list(game.mainline()))
    extra_moves, last_move, move = 0, 0, 0
    end_of_opening = False
    previous_node = node_by_fen(root_fen, graph)
    while extra_moves < 4 or not end_of_opening:
        end_of_opening = True
        if move < total_moves:
            end_of_opening = False
            node = get_opening_node(game, move, user_name, graph)
            if node is not None:
                end_of_opening = False
                graph.add_node(node)
                if previous_node is not None:
                    handle_edging(previous_node, node, graph)
                previous_node = node
                extra_moves = 0
            else:
                extra_moves += 1
        else:
            break
        move += 1


def process_games(chess_games: ChessGames, trees: Dict[str, nx.DiGraph]):
    """Processes all games of the user into the two trees"""
    games = chess_games.games
    user_name = chess_games.user_name
    for game_id in trange(len(games)):
        game = games[game_id]
        add_game_to_graph(trees, game, user_name)


def graph_presentation(graph: nx.DiGraph) -> dict:
    # total_occ = sum([nd.occurrence for nd in graph.nodes])
    nodes = [(nd.name, nd.occurrence, nd.wins / nd.occurrence, nd.fen) for nd in graph.nodes]
    edges = [(edge[0].name, edge[1].name, graph[edge[0]][edge[1]]['weight']) for edge in graph.edges]
    return {'nodes': nodes, 'edges': edges}


class GraphBuilder(Resource):
    @staticmethod
    def get():
        s_time = datetime.now()
        print('Handling request...')
        process_games(cg, trees)
        output = {}
        for graph_type in trees.keys():
            graph = trees[graph_type]
            graph_json = graph_presentation(graph)
            output[graph_type] = graph_json
            # print(graph_json)
            # with open('./matyasj' + graph_type + '.json', 'w') as file:
            #     json.dump(graph_json, file)
        print('Done in ', datetime.now() - s_time)
        return output
