import json
import threading
import time
from .message import DESERIALIZE, SERIALIZE, BUILD_MSG, COPY_WITH_DECREMENT_TTL
from .transport import TCP_SERVER, TCP_SEND
from .routing_table import ROUTING_TABLE
from .algorithms.dijkstra import ALGO_DIJKSTRA
from .algorithms.flooding import ALGO_FLOODING
from .algorithms.lsr import ALGO_LSR


# clase nodo para gestionar la lógica de red
class NODE:
    def __init__(self, SELF_ID, NAMES_CFG, TOPO_CFG, ALGO):
        self.SELF_ID = SELF_ID
        self.NAMES = NAMES_CFG["config"]
        self.TOPO = TOPO_CFG["config"]
        self.ALGO_NAME = ALGO
        SELF_EP = self.NAMES[SELF_ID]
        self.SERVER = TCP_SERVER(SELF_EP["host"], int(SELF_EP["port"]), self._on_bytes)

        # descubrimos los vecinos del nodo
        self.NEIGHBORS = list(self.TOPO.get(SELF_ID, []))

        # tabla de enrutamiento
        self.TABLE = ROUTING_TABLE(SELF_ID)

        # algoritmos de enrutamiento
        self.FLOOD = ALGO_FLOODING()
        self.LSR = ALGO_LSR(SELF_ID)
        self.LSR.set_neighbors(self.NEIGHBORS)

        if self.ALGO_NAME == "dijkstra":
            self.DIJK = ALGO_DIJKSTRA(SELF_ID, self.TOPO)
            self.TABLE.set_all(self.DIJK.compute_table())

        # cola
        self._INBOX = []
        self._INBOX_LOCK = threading.Lock()

    # transporte
    def _on_bytes(self, LINE, addr):
        try:
            MSG = DESERIALIZE(LINE)
        except Exception as e:
            print(f"[{self.SELF_ID}] ERROR JSON: {e}")
            return
        with self._INBOX_LOCK:
            self._INBOX.append(MSG)

    # envio a vecinos
    def _send_to(self, NEIGH_ID, MSG):
        EP = self.NAMES.get(NEIGH_ID)
        if not EP:
            return
        # anotar el nodo previo en los headers
        H = dict(MSG.get("headers", {}))
        H["PREV"] = self.SELF_ID
        MSG["headers"] = H
        try:
            TCP_SEND(EP["host"], int(EP["port"]), SERIALIZE(MSG))
        except Exception as e:
            print(f"[{self.SELF_ID}] ERROR ENVÍO {NEIGH_ID}: {e}")

    # api para enviar mensajes
    def send_data(self, DST_ID, TEXT):
        PROTO = self.ALGO_NAME
        M = BUILD_MSG(PROTO, "message", self.SELF_ID, DST_ID, {"text": TEXT})
        self._forward(M, ORIGIN=True)

    # reglas de forwarding según el protocolo
    def _forward(self, MSG, ORIGIN=False):
        if MSG["ttl"] <= 0:
            return
        TYPE = MSG["type"]
        DST = MSG["to"]
        HDR = MSG.get("headers", {})
        PREV = HDR.get("PREV")

        if TYPE == "message" and (DST == self.SELF_ID or DST is None):
            TXT = MSG.get("payload", {}).get("text")
            print(f"[{self.SELF_ID}] MENSAJE RECIBIDO: {TXT}")
            return

        # forwarding según el protocolo
        if self.ALGO_NAME == "flooding":
            MSG2 = COPY_WITH_DECREMENT_TTL(MSG)
            MSG_ID = MSG2["headers"]["MSG_ID"]
            if not self.FLOOD.should_forward(MSG_ID):
                return
            for N in self.NEIGHBORS:
                if N != PREV:
                    self._send_to(N, MSG2)

        elif self.ALGO_NAME == "dijkstra":
            if DST == self.SELF_ID:
                print(f"[{self.SELF_ID}] DATA PARA MÍ (DIJKSTRA).")
                return
            NH = self.TABLE.get_next(DST)
            if NH:
                self._send_to(NH, COPY_WITH_DECREMENT_TTL(MSG))
            else:
                MSG2 = COPY_WITH_DECREMENT_TTL(MSG)
                MSG_ID = MSG2["headers"]["MSG_ID"]
                if not self.FLOOD.should_forward(MSG_ID):
                    return
                for N in self.NEIGHBORS:
                    if N != PREV:
                        self._send_to(N, MSG2)

        elif self.ALGO_NAME == "lsr":
            if TYPE == "message":
                if DST == self.SELF_ID:
                    print(f"[{self.SELF_ID}] DATA PARA MÍ (LSR).")
                    return
                NH = self.TABLE.get_next(DST)
                if NH:
                    self._send_to(NH, COPY_WITH_DECREMENT_TTL(MSG))
                else:
                    MSG2 = COPY_WITH_DECREMENT_TTL(MSG)
                    MSG_ID = MSG2["headers"]["MSG_ID"]
                    if not self.FLOOD.should_forward(MSG_ID):
                        return
                    for N in self.NEIGHBORS:
                        if N != PREV:
                            self._send_to(N, MSG2)

            elif TYPE == "lsp":
                LSP = MSG.get("payload", {})
                if self.LSR.ingest_lsp(LSP):
                    for N in self.NEIGHBORS:
                        if N != PREV:
                            self._send_to(N, COPY_WITH_DECREMENT_TTL(MSG))
                    self.TABLE.set_all(self.LSR.compute_table())

            elif TYPE == "hello":
                ECHO = BUILD_MSG(
                    "lsr", "echo", self.SELF_ID, MSG["from"], {"rx": time.time()}
                )
                self._send_to(PREV, ECHO)

    # hilo forwarding de mensajes
    def _loop_forward(self):
        while True:
            with self._INBOX_LOCK:
                ITEMS = self._INBOX[:]
                self._INBOX.clear()
            for MSG in ITEMS:
                self._forward(MSG)
            time.sleep(0.01)

    # hilo de routing (LSR)
    def _loop_routing(self):
        T0 = 0.0
        T1 = 0.0
        while True:
            NOW = time.time()
            if self.ALGO_NAME == "lsr" and NOW - T0 > 3.0:
                for N in self.NEIGHBORS:
                    H = BUILD_MSG("lsr", "hello", self.SELF_ID, N, {"tx": NOW})
                    self._send_to(N, H)
                T0 = NOW
            if self.ALGO_NAME == "lsr" and NOW - T1 > 5.0:
                LSP = self.LSR.new_lsp()
                M = BUILD_MSG("lsr", "lsp", self.SELF_ID, None, LSP, TTL=12)
                for N in self.NEIGHBORS:
                    self._send_to(N, M)
                self.LSR.ingest_lsp(LSP)
                self.TABLE.set_all(self.LSR.compute_table())
                T1 = NOW
            time.sleep(0.1)

    # arranque del nodo
    def start(self):
        print(
            f"[{self.SELF_ID}] INICIANDO {self.ALGO_NAME.upper()} :: VECINOS={self.NEIGHBORS}"
        )
        self.SERVER.start()
        threading.Thread(target=self._loop_forward, daemon=True).start()
        threading.Thread(target=self._loop_routing, daemon=True).start()

    def stop(self):
        self.SERVER.stop()
