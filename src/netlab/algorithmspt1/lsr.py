from collections import defaultdict
from ..graph import GRAPH, DIJKSTRA_ALL


# link state routing algorithm
class ALGO_LSR:
    def __init__(self, SELF_ID):
        self.SELF_ID = SELF_ID
        self.SEQ = 0
        self.LSDB = defaultdict(dict)
        self.NEIGH_COST = {}

    def set_neighbors(self, NEIGHBORS):
        self.NEIGH_COST = {n: 1 for n in NEIGHBORS}

    def new_lsp(self):
        self.SEQ += 1
        return {
            "node": self.SELF_ID,
            "seq": self.SEQ,
            "neighbors": [{"id": v, "cost": c} for v, c in self.NEIGH_COST.items()],
        }

    def ingest_lsp(self, LSP: dict):
        U = LSP["node"]
        SQ = int(LSP["seq"])
        if U not in self.LSDB or SQ > self.LSDB[U].get("seq", -1):
            self.LSDB[U]["seq"] = SQ
            self.LSDB[U]["nbrs"] = {
                e["id"]: int(e.get("cost", 1)) for e in LSP.get("neighbors", [])
            }
            return True
        return False

    def build_graph(self):
        G = GRAPH()
        for U, REC in self.LSDB.items():
            for V, W in REC.get("nbrs", {}).items():
                G.add_edge(U, V, W)
        return G

    def compute_table(self):
        G = self.build_graph()
        NEXT, _ = DIJKSTRA_ALL(G, self.SELF_ID)
        return NEXT
