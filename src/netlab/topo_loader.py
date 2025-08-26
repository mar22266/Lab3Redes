import json
from pathlib import Path
from typing import Dict, Any, Tuple


def LOAD_TOPOLOGY(
    PATH: str,
) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, Dict[str, int]]]:
    P = Path(PATH).resolve()
    DATA = json.loads(P.read_text(encoding="utf-8"))
    NODES = DATA.get("NODES", {})
    ID_TO_JID = {NID: NODES[NID]["JID"] for NID in NODES}
    NEI_COSTS = {NID: NODES[NID].get("NEIGHBORS", {}) for NID in NODES}
    return DATA, ID_TO_JID, NEI_COSTS
