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

    def __repr__(self):
        string_repr = ""
        
        for source, target_counter in self.graph.items():
            string_repr += f"{source.eco} -> {target_counter}\n"
        
        return string_repr

    def add_opening(self, opening: Opening, head: Opening = None):
        if not head:
            head = self.root
            
        # TODO there's an issue here with the openings not updating as needed
        # for key, value in self.graph.items():
        #     if key == opening:
        #         key += opening
        #     for k, v in value.items():
        #         if k == opening:
        #             k += opening
        #             v += 1

        self.graph[head][opening] += 1

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
