from next_move.openings.opening import Opening
from collections import defaultdict, Counter
from tqdm import tqdm


class Tree:
    def __init__(self):
        self.root = Opening(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
            eco="ROOT",
            name="Root"
        )

        self.graph = defaultdict(Counter)
        self.nodes = {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": self.root}
        self.edges = defaultdict(Counter)

    def __repr__(self):
        string_repr = ""
        
        for parent_node, children in self.edges.items():
            counter = {self.nodes[c]: count for c, count in children.items()}
            string_repr += f"{self.nodes[parent_node]} -> {counter}\n"
        
        return string_repr

    def add_opening(self, opening: Opening, head: Opening):
        if opening.fen in self.nodes:
            self.nodes[opening.fen] += opening
        else:
            self.nodes[opening.fen] = opening
        
        self.edges[head.fen][opening.fen] += 1

    def most_common_child(self, opening: Opening, n: int = 1):
        return self.graph[opening].most_common(n)

    def to_sankey(self) -> tuple[set[Opening], list[dict]]:
        sankey_links = []
        sankey_nodes = set()
        for source, target_counter in self.graph.items():
            sankey_nodes.add(source)
            for target, count in dict(target_counter).items():
                sankey_links.append(
                    {
                        "source": source,
                        "target": target,
                        "count": count
                    }
                )
                sankey_nodes.add(target)
        return sankey_nodes, sankey_links
