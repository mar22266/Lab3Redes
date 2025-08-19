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

