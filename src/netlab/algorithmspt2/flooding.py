from typing import Dict, Any, Tuple


class FLOODING_ALGO:
    def __init__(self, MY_NODE_ID: str):
        self.MY_NODE_ID = MY_NODE_ID

    def HANDLE_INFO(self, MSG: Dict[str, Any]) -> None:
        return

    def HANDLE_HELLO(self, MSG: Dict[str, Any]) -> None:
        return

    def NEXT_HOP_FOR(self, DEST_NODE_ID: str) -> str | None:
        return None
