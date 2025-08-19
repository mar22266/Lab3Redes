import socket
import threading


# clase para el servidor TCP
class TCP_SERVER:
    def __init__(self, HOST, PORT, ON_MESSAGE):
        self.HOST = HOST
        self.PORT = PORT
        self.ON_MESSAGE = ON_MESSAGE
        self._stop = threading.Event()
        self.TH = None

    def start(self):
        def run():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.HOST, self.PORT))
                s.listen()
                while not self._stop.is_set():
                    try:
                        s.settimeout(0.5)
                        conn, addr = s.accept()
                    except socket.timeout:
                        continue
                    threading.Thread(
                        target=self._handle, args=(conn, addr), daemon=True
                    ).start()

        self.TH = threading.Thread(target=run, daemon=True)
        self.TH.start()

    def _handle(self, conn, addr):
        with conn:
            BUFF = b""
            while True:
                CHUNK = conn.recv(4096)
                if not CHUNK:
                    break
                BUFF += CHUNK
                while b"\n" in BUFF:
                    LINE, BUFF = BUFF.split(b"\n", 1)
                    if LINE.strip():
                        try:
                            self.ON_MESSAGE(LINE, addr)
                        except Exception as e:
                            print(f"[SERVER ERROR] {e}")

    def stop(self):
        self._stop.set()


def TCP_SEND(HOST, PORT, DATA_BYTES):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.settimeout(1.5)
        c.connect((HOST, PORT))
        c.sendall(DATA_BYTES)
