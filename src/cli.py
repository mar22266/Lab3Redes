import argparse
import json
import time
from .node import NODE


# cargar un JSON desde un archivo
def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# funcion main para arrancar el cliente del nodo
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="ID DEL NODO (EJ: A)")
    ap.add_argument("--algo", required=True, choices=["flooding", "dijkstra", "lsr"])
    ap.add_argument("--topo", required=True, help="RUTA TOPO JSON")
    ap.add_argument("--names", required=True, help="RUTA NAMES JSON")
    ap.add_argument(
        "--send",
        action="store_true",
        help="ENVIAR MENSAJE Y SALIR (NO ARRANCA SERVIDOR)",
    )
    ap.add_argument("--to", help="DESTINO DEL MENSAJE")
    ap.add_argument("--text", help="TEXTO DEL MENSAJE")
    args = ap.parse_args()

    topo_cfg = _load_json(args.topo)
    names_cfg = _load_json(args.names)

    # crear el nodo
    node = NODE(args.id, names_cfg, topo_cfg, args.algo)

    # envio de mensajes
    if args.send:
        if not args.to or not args.text:
            raise SystemExit("--send requiere --to y --text")
        print(f"[{args.id}] ENVIANDO ({args.algo.upper()}) -> [{args.to}]: {args.text}")
        time.sleep(0.1)
        node.send_data(args.to, args.text)
        time.sleep(0.5)
        print(f"[{args.id}] ENVÍO COMPLETADO -> [{args.to}]")
        return

    node.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        node.stop()


if __name__ == "__main__":
    main()
