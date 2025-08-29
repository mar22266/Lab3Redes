# Laboratorio 3

## Integrantes

- Sergio Orellana 221122
- Andre Marroquin 22266
- Carlos Valladdares 221164

# Routing Lab – Fase 1 (Sockets)

Implementaciones de **Dijkstra**, **Flooding** y **Link State Routing (LSR)** con mensajes JSON,
hilos de **forwarding** y **routing**, y ejecución local por sockets TCP.

## Requisitos

- Python 3.10+
- Wsl

## Qué incluye cada algoritmo (Fase 1)

- **Flooding**: Conjunto `SEEN` para evitar reenvíos duplicados; uso de `TTL`; evita enviar al `PREV`.
- **Dijkstra**: Construcción de **GRAPH** desde `topo-*.json` y cómputo de `NEXT-HOP` por destino.
- **LSR**: Emisión periódica de `HELLO` (3s) y `LSP` (5s), base de datos de estado de enlace, grafo y Dijkstra local.  
  Todo respetando el **modelo de mensajes** y los **roles forwarding/routing** en paralelo. :contentReference[oaicite:6]{index=6}

# Ejecución con `make` y pruebas – Fase 1 (Flooding, Dijkstra, LSR)

## Targets principales

- `make flood-all` → inicia A, B, C y D en modo **Flooding**.
- `make dijkstra-all` → inicia A, B, C y D en modo **Dijkstra**.
- `make lsr-all` → inicia A, B, C y D en modo **LSR**.
- `make send-flooding` → envía **A → D** un mensaje de prueba en Flooding.
- `make send-dijkstra` → envía **A → D** en Dijkstra.
- `make send-lsr` → espera ~8 s y envía **A → D** en LSR.
- `make ps` → lista procesos activos del laboratorio.
- `make stop` → detiene todos los nodos del laboratorio.

# Routing Lab – Fase 2 (Redis Pub/Sub)

La red se implementa con Redis Pub/Sub remoto.
Cada nodo es un proceso Python que publica/suscribe en canales Redis (uno por nodo).
Se implementan y prueban los 3 algoritmos sobre Redis:

- Flooding (Redis)
- Distance Vector – DV (Redis)
- Link State Routing – LSR (Redis)

se respetó al 100% el protocolo de mensajes indicado.

- Requisitos (Fase 2)
- Python 3.12 recomendado (funciona 3.10+)
- Entorno virtual
- Acceso Redis remoto (proveído)

# Instalación rápida

```
cd ~/Lab3Redes
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

# Protocolo de mensajes

```
{
  "proto": "lsr|dv|flooding",
  "type": "hello|info|message",
  "from": "sec20.topologia1.node2",     
  "to": "broadcast|sec20.topologia1.node1",
  "ttl": 5,
  "headers": ["A","B","C"],     
  "payload": { ... } | "texto"
}
```

# Ejecución y pruebas – Fase 2 general se le cambia el agoritmo dependiendo el que se decida usar al igual que si se desea usar broadcast se le cambian parametros
B y C receptores en terminales distintas se prueba
```
netlab-redis --redis configs/redis.json --topo configs/topology.json --id B --proto lsr --verbose

netlab-redis --redis configs/redis.json --topo configs/topology.json --id C --proto lsr --verbose
```

A emisor (unicast a C)

```
netlab-redis --redis configs/redis.json --topo configs/topology.json --id A --proto lsr --send-to sec20.topologia1.nodo1 --text "HOLA DESDE A (LSR)" --exit-after-send --verbose
```


