SHELL := /bin/bash
PY ?= python3

.PHONY: run-A run-B run-C run-D flood-all dijkstra-all lsr-all \
        flood-bcd dijkstra-bcd lsr-bcd \
        send-flooding send-dijkstra send-lsr stop check ps

ARGS_TOPO=--topo configs/topo-sample.json
ARGS_NAMES=--names configs/names-sample.json

check:
	@command -v $(PY) >/dev/null || { echo " No se encontró '$(PY)'. Instala con: sudo apt install -y python3"; exit 1; }
	@command -v make >/dev/null || { echo " No se encontró 'make'. Instala con: sudo apt install -y make"; exit 1; }

run-A:
	$(PY) -m src.cli --id A $(ALG) $(ARGS_TOPO) $(ARGS_NAMES)

run-B:
	$(PY) -m src.cli --id B $(ALG) $(ARGS_TOPO) $(ARGS_NAMES)

run-C:
	$(PY) -m src.cli --id C $(ALG) $(ARGS_TOPO) $(ARGS_NAMES)

run-D:
	$(PY) -m src.cli --id D $(ALG) $(ARGS_TOPO) $(ARGS_NAMES)

flood-all: check
	$(MAKE) ALG="--algo flooding" run-A & \
	$(MAKE) ALG="--algo flooding" run-B & \
	$(MAKE) ALG="--algo flooding" run-C & \
	$(MAKE) ALG="--algo flooding" run-D ; wait

dijkstra-all: check
	$(MAKE) ALG="--algo dijkstra" run-A & \
	$(MAKE) ALG="--algo dijkstra" run-B & \
	$(MAKE) ALG="--algo dijkstra" run-C & \
	$(MAKE) ALG="--algo dijkstra" run-D ; wait

lsr-all: check
	$(MAKE) ALG="--algo lsr" run-A & \
	$(MAKE) ALG="--algo lsr" run-B & \
	$(MAKE) ALG="--algo lsr" run-C & \
	$(MAKE) ALG="--algo lsr" run-D ; wait

flood-bcd: check
	$(MAKE) ALG="--algo flooding" run-B & \
	$(MAKE) ALG="--algo flooding" run-C & \
	$(MAKE) ALG="--algo flooding" run-D ; wait

dijkstra-bcd: check
	$(MAKE) ALG="--algo dijkstra" run-B & \
	$(MAKE) ALG="--algo dijkstra" run-C & \
	$(MAKE) ALG="--algo dijkstra" run-D ; wait

lsr-bcd: check
	$(MAKE) ALG="--algo lsr" run-B & \
	$(MAKE) ALG="--algo lsr" run-C & \
	$(MAKE) ALG="--algo lsr" run-D ; wait

send-flooding: check
	$(PY) -m src.cli --id A --algo flooding $(ARGS_TOPO) $(ARGS_NAMES) --send --to D --text "FLOOD-OK"

send-dijkstra: check
	$(PY) -m src.cli --id A --algo dijkstra $(ARGS_TOPO) $(ARGS_NAMES) --send --to D --text "DIJKSTRA-OK"

send-lsr: check
	sleep 8 && $(PY) -m src.cli --id A --algo lsr $(ARGS_TOPO) $(ARGS_NAMES) --send --to D --text "LSR-OK"

ps:
	pgrep -fa "$(PY) -m src.cli" || true

stop:
	pkill -f "$(PY) -m src.cli" || pkill -f "python.* -m src.cli" || true
