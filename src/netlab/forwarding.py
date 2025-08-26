from typing import Dict, Any, List


def SHOULD_DROP_FOR_CYCLE(MSG: Dict[str, Any], MY_NODE_ID: str) -> bool:
    HEADERS = MSG.get("headers", []) or []
    return MY_NODE_ID in HEADERS


def UPDATE_HEADERS_FOR_FORWARD(MSG, MY_NODE_ID):
    hs = list(MSG.get("headers", []) or [])
    if len(hs) >= 3:
        hs.pop(0)
    hs.append(MY_NODE_ID)
    MSG["headers"] = hs


def DEC_TTL(MSG: Dict[str, Any]) -> None:
    MSG["ttl"] = max(0, int(MSG.get("ttl", 0)) - 1)


def FORWARD_TARGETS(
    MSG: Dict[str, Any],
    NEIGHBORS: Dict[str, str],
    INCOMING_ID: str | None,
    NEXT_HOP_JID: str | None,
) -> List[str]:
    TO = MSG.get("to")
    if isinstance(TO, str) and TO.lower() == "broadcast":
        return [jid for nid, jid in NEIGHBORS.items() if nid != INCOMING_ID]
    else:
        return [NEXT_HOP_JID] if NEXT_HOP_JID else []


def CLEAN_INTERNAL(MSG):
    MSG.pop("from_jid", None)
    MSG.pop("from_node_id", None)
    return MSG
