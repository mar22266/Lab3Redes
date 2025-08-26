# -*- coding: utf-8 -*-
import ujson as json
from typing import Dict, Any, List

PROTO_ALLOWED = {"flooding", "dv", "lsr"}
TYPE_ALLOWED = {"hello", "info", "message"}


def _CLAMP_HEADERS(HEADERS: List[str]) -> List[str]:
    return HEADERS[-3:] if len(HEADERS) > 3 else HEADERS


def MAKE_MSG(
    PROTO: str,
    TYPE: str,
    FROM_JID: str,
    TO: str,
    TTL: int,
    HEADERS: List[str],
    PAYLOAD: Any,
) -> Dict[str, Any]:
    assert PROTO in PROTO_ALLOWED, "PROTO INVALIDO"
    assert TYPE in TYPE_ALLOWED, "TYPE INVALIDO"
    assert isinstance(TTL, int) and TTL >= 0, "TTL INVALIDO"
    return {
        "proto": PROTO,
        "type": TYPE,
        "from": FROM_JID,
        "to": TO,
        "ttl": TTL,
        "headers": _CLAMP_HEADERS(list(HEADERS)),
        "payload": PAYLOAD,
    }


def IS_BROADCAST(TO: str) -> bool:
    return isinstance(TO, str) and TO.lower() == "broadcast"


def SERIALIZE(MSG: Dict[str, Any]) -> str:
    return json.dumps(MSG, ensure_ascii=False)


def PARSE(BODY: str) -> Dict[str, Any]:
    OBJ = json.loads(BODY)
    if OBJ.get("proto") not in PROTO_ALLOWED:
        raise ValueError("PROTO INVALIDO")
    if OBJ.get("type") not in TYPE_ALLOWED:
        raise ValueError("TYPE INVALIDO")
    if not isinstance(OBJ.get("ttl"), int):
        raise ValueError("TTL INVALIDO")
    if "headers" not in OBJ or not isinstance(OBJ["headers"], list):
        raise ValueError("HEADERS INVALIDO")
    return OBJ
