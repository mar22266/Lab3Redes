import threading


# clase para la tabla de enrutamiento
class ROUTING_TABLE:
    def __init__(self, SELF_ID):
        self.SELF_ID = SELF_ID
        self._LOCK = threading.Lock()
        self.NEXT = {}

    def set_all(self, M):
        with self._LOCK:
            self.NEXT = dict(M)

    def get_next(self, DST):
        with self._LOCK:
            return self.NEXT.get(DST)

    def __repr__(self):
        with self._LOCK:
            return f"ROUTING_TABLE({self.NEXT})"
