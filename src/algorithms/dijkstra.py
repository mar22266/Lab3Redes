from ..graph import GRAPH, DIJKSTRA_ALL


# Clase para el algoritmo de Dijkstra
class ALGO_DIJKSTRA:
    def __init__(self, SELF_ID, TOPO_CONFIG):
        self.SELF_ID = SELF_ID
        self.TOPO = TOPO_CONFIG
        self.GRAPH = GRAPH()
        for U, LST in self.TOPO.items():
            for V in LST:
                self.GRAPH.add_edge(U, V, 1)

    def compute_table(self):
        NEXT, _ = DIJKSTRA_ALL(self.GRAPH, self.SELF_ID)
        return NEXT
