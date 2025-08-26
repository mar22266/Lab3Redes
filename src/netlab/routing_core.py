import asyncio
from typing import Dict, Any, Callable
from .common_protocol import MAKE_MSG, SERIALIZE, PARSE, IS_BROADCAST
from .forwarding import (
    SHOULD_DROP_FOR_CYCLE,
    UPDATE_HEADERS_FOR_FORWARD,
    DEC_TTL,
    FORWARD_TARGETS,
    CLEAN_INTERNAL,
)


class ROUTING_CORE:
    def __init__(
        self,
        MY_NODE_ID: str,
        MY_JID: str,
        PROTO: str,
        ID_TO_JID: Dict[str, str],
        NEIGHBORS_COSTS: Dict[str, int],
        SEND_FUNC: Callable[[str, str], None],
        ALGO,
    ):
        self.MY_NODE_ID = MY_NODE_ID
        self.MY_JID = MY_JID
        self.PROTO = PROTO
        self.ID_TO_JID = dict(ID_TO_JID)
        self.NEIGHBORS_COSTS = dict(NEIGHBORS_COSTS)  # {NID: COST}
        self.NEIGHBOR_IDS = list(self.NEIGHBORS_COSTS.keys())
        self.NEIGHBOR_JIDS = {nid: self.ID_TO_JID[nid] for nid in self.NEIGHBOR_IDS}
        self.SEND = SEND_FUNC
        self.ALGO = ALGO
        self.INBOX: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()

    async def ON_XMPP_MESSAGE(self, FROM_JID: str, BODY: str):
        try:
            MSG = PARSE(BODY)
        except Exception:
            return
        MSG["from_jid"] = FROM_JID
        MSG["from_node_id"] = self._NODE_ID_BY_JID(FROM_JID)
        await self.INBOX.put(MSG)

    def _NODE_ID_BY_JID(self, JID: str) -> str | None:
        JLOW = (JID or "").lower()
        for NID, JJ in self.ID_TO_JID.items():
            if JJ.lower() == JLOW:
                return NID
        return None

    async def LOOP_FORWARDING(self):
        while True:
            MSG = await self.INBOX.get()
            TTL = int(MSG.get("ttl", 0))
            if TTL <= 0:
                continue

            TYP = MSG.get("type")
            INCOMING_ID = MSG.get("from_node_id")

            if TYP == "hello":
                if hasattr(self.ALGO, "HANDLE_HELLO"):
                    self.ALGO.HANDLE_HELLO(MSG)
                continue

            if TYP == "info":
                if hasattr(self.ALGO, "HANDLE_INFO"):
                    self.ALGO.HANDLE_INFO(MSG)

                DEC_TTL(MSG)
                if int(MSG.get("ttl", 0)) <= 0:
                    continue
                if SHOULD_DROP_FOR_CYCLE(MSG, self.MY_NODE_ID):
                    continue
                UPDATE_HEADERS_FOR_FORWARD(MSG, self.MY_NODE_ID)

                TARGETS = FORWARD_TARGETS(MSG, self.NEIGHBOR_JIDS, INCOMING_ID, None)

                OUT = dict(MSG)
                CLEAN_INTERNAL(OUT)
                WIRE = SERIALIZE(OUT)

                for TJ in TARGETS:
                    self.SEND(TJ, WIRE)
                continue

            if TYP == "message":
                DEST = MSG.get("to")
                if isinstance(DEST, str) and DEST.lower() == self.MY_JID.lower():
                    print(f"[DATA PARA MI {self.MY_NODE_ID}] {MSG.get('payload')}")
                    continue

                DEST_NODE_ID = (
                    self._NODE_ID_BY_JID(DEST)
                    if (isinstance(DEST, str) and DEST.lower() != "broadcast")
                    else None
                )
                NEXT_HOP_NODE_ID = None
                if DEST_NODE_ID and hasattr(self.ALGO, "NEXT_HOP_FOR"):
                    NEXT_HOP_NODE_ID = self.ALGO.NEXT_HOP_FOR(DEST_NODE_ID)
                NEXT_HOP_JID = (
                    self.ID_TO_JID.get(NEXT_HOP_NODE_ID) if NEXT_HOP_NODE_ID else None
                )

                DEC_TTL(MSG)
                if int(MSG.get("ttl", 0)) <= 0:
                    continue
                if SHOULD_DROP_FOR_CYCLE(MSG, self.MY_NODE_ID):
                    continue
                UPDATE_HEADERS_FOR_FORWARD(MSG, self.MY_NODE_ID)
                TARGETS = FORWARD_TARGETS(
                    MSG, self.NEIGHBOR_JIDS, INCOMING_ID, NEXT_HOP_JID
                )
                OUT = dict(MSG)
                CLEAN_INTERNAL(OUT)
                WIRE = SERIALIZE(OUT)
                for TJ in TARGETS:
                    self.SEND(TJ, WIRE)
                continue

    def BUILD_INFO_PAYLOAD(self) -> dict:
        if self.PROTO == "dv":
            DIST = getattr(self.ALGO, "DIST", {})
            return {"DISTANCES": DIST}
        elif self.PROTO == "lsr":
            return {"LINKS": {self.MY_NODE_ID: self.NEIGHBORS_COSTS}}
        else:
            return {}

    def MAKE_HELLO(self) -> dict:
        return MAKE_MSG(self.PROTO, "hello", self.MY_JID, "broadcast", 5, [], "")

    def MAKE_INFO(self, _NEI_COSTS: Dict[str, int]) -> dict:
        return MAKE_MSG(
            self.PROTO,
            "info",
            self.MY_JID,
            "broadcast",
            5,
            [],
            self.BUILD_INFO_PAYLOAD(),
        )

    def MAKE_MESSAGE(self, TO_JID: str, TEXT: str) -> dict:
        return MAKE_MSG(self.PROTO, "message", self.MY_JID, TO_JID, 5, [], TEXT)
