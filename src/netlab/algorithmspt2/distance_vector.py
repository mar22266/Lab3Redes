from typing import Dict, Any, Tuple

INF = 10**9


class DISTANCE_VECTOR_ALGO:
    def __init__(self, MY_NODE_ID: str, INIT_NEI_COSTS: Dict[str, int]):
        self.MY_NODE_ID = MY_NODE_ID
        self.DIST: Dict[str, int] = {MY_NODE_ID: 0}
        self.NEXT: Dict[str, str] = {}
        self.C_NEI = dict(INIT_NEI_COSTS)

        for NID, C in self.C_NEI.items():
            self.DIST[NID] = C
            self.NEXT[NID] = NID

    def HANDLE_HELLO(self, MSG: Dict[str, Any]) -> None:
        return

    def HANDLE_INFO(self, MSG: Dict[str, Any]) -> None:
        FROM = MSG.get("from_node_id")
        if not FROM:
            return
        PAY = MSG.get("payload", {}) or {}
        DV = PAY.get("DISTANCES", {})
        C_TO_FROM = self.C_NEI.get(FROM, INF)

        UPDATED = False
        for DEST, COST_VIA_FROM in DV.items():
            COST_VIA = C_TO_FROM + int(COST_VIA_FROM)
            CURR = self.DIST.get(DEST, INF)
            if COST_VIA < CURR:
                self.DIST[DEST] = COST_VIA
                self.NEXT[DEST] = FROM
                UPDATED = True

    def NEXT_HOP_FOR(self, DEST_NODE_ID: str) -> str | None:
        return self.NEXT.get(DEST_NODE_ID)
