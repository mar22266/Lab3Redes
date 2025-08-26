import asyncio
import json
from pathlib import Path
from typing import Dict, Any

import redis.asyncio as redis

from .routing_core import ROUTING_CORE
from .common_protocol import SERIALIZE, PARSE
from .topo_loader import LOAD_TOPOLOGY
from .algorithmspt2.distance_vector import DISTANCE_VECTOR_ALGO
from .algorithmspt2.link_state import LINK_STATE_ALGO
from .algorithmspt2.flooding import FLOODING_ALGO

# ejecucion
# netlab-redis --redis configs/redis.json --topo configs/topology.json --id B --proto lsr --verbose
# netlab-redis --redis configs/redis.json --topo configs/topology.json --id C --proto lsr --verbose

# netlab-redis --redis configs/redis.json --topo configs/topology.json \
#  --id A --proto lsr \
#  --send-to channel:nodeC --text "HOLA DESDE A (LSR REDIS)" --verbose


def LOAD_JSON(PATH: str) -> Dict[str, Any]:
    P = Path(PATH).resolve()
    return json.loads(P.read_text(encoding="utf-8"))


async def START_NODE_REDIS(
    RCFG: Dict[str, Any],
    CORE: ROUTING_CORE,
    HELLO_INT: int,
    INFO_INT: int,
    VERBOSE: bool,
    SKIP_HELLO: bool,
    SKIP_INFO: bool,
):
    R = redis.Redis(
        host=RCFG["HOST"],
        port=int(RCFG.get("PORT", 6379)),
        password=RCFG.get("PASSWORD", None),
        decode_responses=False,
    )

    async with R.pubsub() as PUBSUB:
        await PUBSUB.subscribe(CORE.MY_JID)

        async def READER():
            while True:
                MSG = await PUBSUB.get_message(
                    ignore_subscribe_messages=True, timeout=None
                )
                if MSG is None:
                    await asyncio.sleep(0.01)
                    continue
                RAW = MSG.get("data")
                BODY = (
                    RAW.decode(errors="replace")
                    if isinstance(RAW, (bytes, bytearray))
                    else str(RAW)
                )

                try:
                    OBJ = PARSE(BODY)
                    FROM_JID = str(OBJ.get("from", "unknown"))
                    if VERBOSE:
                        print(f"[RECV {CORE.MY_NODE_ID}] {BODY}")
                except Exception:
                    continue

                await CORE.ON_XMPP_MESSAGE(FROM_JID, BODY)

        async def SENDER(TO_JID: str, BODY: str):
            if VERBOSE:
                print(f"[SEND {CORE.MY_NODE_ID} -> {TO_JID}] {BODY}")
            await R.publish(TO_JID, BODY)

        CORE.SEND = lambda TO, BODY: asyncio.create_task(SENDER(TO, BODY))

        asyncio.create_task(CORE.LOOP_FORWARDING())

        if not SKIP_HELLO:

            async def HELLO_LOOP():
                while True:
                    await asyncio.sleep(max(1, HELLO_INT))
                    MSG = CORE.MAKE_HELLO()
                    WIRE = SERIALIZE(MSG)
                    for NJID in CORE.NEIGHBOR_JIDS.values():
                        CORE.SEND(NJID, WIRE)

            asyncio.create_task(HELLO_LOOP())

        if not SKIP_INFO:

            async def INFO_LOOP():
                while True:
                    await asyncio.sleep(max(1, INFO_INT))
                    MSG = CORE.MAKE_INFO(CORE.NEIGHBORS_COSTS)
                    WIRE = SERIALIZE(MSG)
                    for NJID in CORE.NEIGHBOR_JIDS.values():
                        CORE.SEND(NJID, WIRE)

            asyncio.create_task(INFO_LOOP())

        await READER()


def MAIN():
    import argparse

    PAR = argparse.ArgumentParser(
        description="NETLAB sobre Redis (Flooding / DV / LSR)"
    )
    PAR.add_argument("--redis", default="configs/redis.json", help="Ruta config Redis")
    PAR.add_argument("--topo", default="configs/topology.json", help="Ruta topología")
    PAR.add_argument("--id", required=True, help="ID del nodo (A, B, C, ...)")
    PAR.add_argument(
        "--proto", required=True, choices=["flooding", "dv", "lsr"], help="Algoritmo"
    )
    PAR.add_argument(
        "--hello-interval", type=int, default=6, help="Segundos entre HELLO"
    )
    PAR.add_argument("--info-interval", type=int, default=8, help="Segundos entre INFO")
    PAR.add_argument(
        "--send-to", default="", help="Canal destino (JID en la topología)"
    )
    PAR.add_argument("--text", default="", help="Texto del MESSAGE")
    PAR.add_argument(
        "--verbose", action="store_true", help="Imprime tráfico en consola"
    )
    # SKIPS DE PRUEBA
    PAR.add_argument("--skip-hello", action="store_true", help="No emite HELLO")
    PAR.add_argument("--skip-info", action="store_true", help="No emite INFO")
    PAR.add_argument(
        "--exit-after-send",
        action="store_true",
        help="Si se envía MESSAGE, salir al terminar",
    )

    ARGS = PAR.parse_args()

    RCFG = LOAD_JSON(ARGS.redis)
    _TCFG, ID_TO_JID, NEI_COSTS_ALL = LOAD_TOPOLOGY(ARGS.topo)

    MY_NODE_ID = ARGS.id
    MY_JID = ID_TO_JID[MY_NODE_ID]
    MY_NEI_COSTS = NEI_COSTS_ALL[MY_NODE_ID]

    if ARGS.proto == "flooding":
        ALGO = FLOODING_ALGO(MY_NODE_ID)
    elif ARGS.proto == "dv":
        ALGO = DISTANCE_VECTOR_ALGO(MY_NODE_ID, MY_NEI_COSTS)
    else:
        ALGO = LINK_STATE_ALGO(MY_NODE_ID)

    CORE = ROUTING_CORE(
        MY_NODE_ID=MY_NODE_ID,
        MY_JID=MY_JID,
        PROTO=ARGS.proto,
        ID_TO_JID=ID_TO_JID,
        NEIGHBORS_COSTS=MY_NEI_COSTS,
        SEND_FUNC=lambda to, body: None,
        ALGO=ALGO,
    )

    async def RUN():
        task = asyncio.create_task(
            START_NODE_REDIS(
                RCFG=RCFG,
                CORE=CORE,
                HELLO_INT=int(ARGS.hello_interval),
                INFO_INT=int(ARGS.info_interval),
                VERBOSE=bool(ARGS.verbose),
                SKIP_HELLO=bool(ARGS.skip_hello),
                SKIP_INFO=bool(ARGS.skip_info),
            )
        )

        if ARGS.send_to and ARGS.text:
            await asyncio.sleep(2)
            DATA = CORE.MAKE_MESSAGE(TO_JID=ARGS.send_to, TEXT=ARGS.text)

            if isinstance(ARGS.send_to, str) and ARGS.send_to.lower() == "broadcast":
                WIRE = SERIALIZE(DATA)
                for NJID in CORE.NEIGHBOR_JIDS.values():
                    CORE.SEND(NJID, WIRE)
            else:
                WIRE = SERIALIZE(DATA)
                CORE.SEND(ARGS.send_to, WIRE)

            if ARGS.exit_after_send:
                await asyncio.sleep(1)
                return

        await task

    asyncio.run(RUN())


if __name__ == "__main__":
    MAIN()
