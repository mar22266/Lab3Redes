import heapq
from collections import defaultdict


# grafo y dijkstra utilitario
class GRAPH:
    def __init__(self):
        self.ADJ = defaultdict(dict)  #

    def add_edge(self, U, V, W=1):
        self.ADJ[U][V] = W
        self.ADJ[V][U] = W

    def neighbors(self, U):
        return self.ADJ[U].items()


def DIJKSTRA_ALL(G: GRAPH, SRC: str):
    DIST = {SRC: 0}
    PREV = {}
    PQ = [(0, SRC)]
    while PQ:
        D, U = heapq.heappop(PQ)
        if D != DIST.get(U, float("inf")):
            continue
        for V, W in G.neighbors(U):
            ND = D + W
            if ND < DIST.get(V, float("inf")):
                DIST[V] = ND
                PREV[V] = U
                heapq.heappush(PQ, (ND, V))

    NEXT = {}
    for DST in DIST.keys():
        if DST == SRC:
            continue
        if DST not in PREV:
            continue

        if PREV[DST] == SRC:
            NEXT[DST] = DST
            continue

        CUR = DST
        while PREV.get(CUR) is not None and PREV[CUR] != SRC:
            CUR = PREV[CUR]
        NEXT[DST] = CUR

    return NEXT, DIST
