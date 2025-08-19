import time


# flooding con TTL y sin duplicacion de mensajes
class ALGO_FLOODING:
    def __init__(self):
        self.SEEN = {}

    def should_forward(self, MSG_ID):
        NOW = time.time()
        for K in list(self.SEEN.keys()):
            if NOW - self.SEEN[K] > 60:
                self.SEEN.pop(K, None)
        if MSG_ID in self.SEEN:
            return False
        self.SEEN[MSG_ID] = NOW
        return True
