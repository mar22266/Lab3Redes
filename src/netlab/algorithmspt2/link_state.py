from typing import Dict, Any
import networkx as nx


class LINK_STATE_ALGO:
    def __init__(self, MY_NODE_ID: str):
        self.MY_NODE_ID = MY_NODE_ID
        self.G = nx.Graph()

    def HANDLE_HELLO(self, MSG: Dict[str, Any]) -> None:
        return

    def HANDLE_INFO(self, MSG: Dict[str, Any]) -> None:
        PAY = MSG.get("payload", {}) or {}
        LINKS = PAY.get("LINKS", {})
        for A, NEI in LINKS.items():
            for B, C in NEI.items():
                self.G.add_edge(A, B, weight=int(C))

    def NEXT_HOP_FOR(self, DEST_NODE_ID: str) -> str | None:
        if self.MY_NODE_ID == DEST_NODE_ID:
            return DEST_NODE_ID
        try:
            PATH = nx.shortest_path(
                self.G, self.MY_NODE_ID, DEST_NODE_ID, weight="weight"
            )
            if len(PATH) >= 2:
                return PATH[1]
            return None
        except Exception:
            return None
