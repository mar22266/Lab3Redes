import json
import time
import uuid

# Constants for message protocol
DEFAULT_TTL = 8


def BUILD_MSG(PROTO, TYPE, FROM_ID, TO_ID, PAYLOAD=None, TTL=DEFAULT_TTL, HEADERS=None):
    MSG = {
        "proto": str(PROTO),
        "type": str(TYPE),
        "from": str(FROM_ID),
        "to": str(TO_ID) if TO_ID is not None else None,
        "ttl": int(TTL),
        "headers": HEADERS or {},
        "payload": PAYLOAD,
        "ts": time.time(),
    }
    if "MSG_ID" not in MSG["headers"]:
        MSG["headers"]["MSG_ID"] = str(uuid.uuid4())
    return MSG


def SERIALIZE(MSG: dict) -> bytes:
    return (json.dumps(MSG, separators=(",", ":")) + "\n").encode("utf-8")


def DESERIALIZE(B: bytes) -> dict:
    return json.loads(B.decode("utf-8"))


def COPY_WITH_DECREMENT_TTL(MSG: dict) -> dict:
    C = dict(MSG)
    C["ttl"] = max(0, MSG.get("ttl", DEFAULT_TTL) - 1)
    return C
