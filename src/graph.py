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
    for DST in DIST:
        if DST == SRC:
            continue
        CUR = DST
        PATH = [CUR]
        while CUR in PREV and PREV[CUR] != SRC:
            CUR = PREV[CUR]
            PATH.append(CUR)
        if DST in PREV:
            NH = DST if PREV[DST] == SRC else PREV[CUR]
            NEXT[DST] = NH if PREV.get(NH, SRC) == SRC else NH
    return NEXT, DIST
