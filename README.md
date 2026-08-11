# DVR TLS Device Server

An asynchronous Python TLS server for DVR / IP-camera device registration and live presence tracking.

Devices connect over TLS, send a custom `DssProtocol` registration payload (JSON wrapped in an HTTP POST), and stay online via heartbeats. The server keeps **hot state in Redis**, **durable records in MySQL**, and drops idle clients after a configurable timeout — the kind of dual-store, long-lived connection pattern used in real surveillance and IoT backends.

---

## Why this project

Surveillance and IoT fleets need a control plane that can:

- Accept many concurrent device connections over TLS
- Register / update device metadata in real time
- Know which devices are online right now vs historically
- Clean up cleanly on timeout or disconnect

This repo implements that control plane as a focused, readable Python service — built to demonstrate concurrent networking, protocol handling, and production-minded state management.

---

## Highlights

| Area | What you'll find |
|------|------------------|
| **Concurrency** | `asyncio` + TLS (`ssl`) with per-connection sessions and heartbeat timeouts |
| **Protocol** | Custom `DssProtocol` registration request/response over TLS |
| **Hot path** | Redis hashes + TTL for live device presence |
| **Cold path** | MySQL via Tortoise ORM — device upserts + structured event logs |
| **Ops** | Rotating file logs (Loguru), configurable timeouts, sample + load-test clients |
| **Load harness** | Clustered client that can simulate tens of thousands of device sessions |

---

## Architecture

```text
┌─────────────┐   TLS + HTTP POST (JSON)   ┌──────────────────┐
│ DVR / camera│ ─────────────────────────► │  asyncio TLS     │
│   devices   │ ◄───────────────────────── │  server          │
└─────────────┘   MSG_DEV_REGISTER_RSP     │  (tls_server.py) │
                                           └────────┬─────────┘
                                                    │
                                           process_message()
                                                    │
                          ┌─────────────────────────┼─────────────────────────┐
                          ▼                         ▼                         ▼
                   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
                   │    Redis    │          │    MySQL    │          │ DeviceLog   │
                   │ live presence│         │ Device row  │          │  audit trail│
                   │  + key TTL  │          │   upsert    │          │  (register /│
                   └─────────────┘          └─────────────┘          │  disconnect)│
                                                                     └─────────────┘
```

**Data split**

- **Redis** — “is this serial online, and from which IP?” (ephemeral, TTL-backed)
- **MySQL** — durable device profile + event history for later inspection

On disconnect or heartbeat timeout, the session is cleared from Redis, the device is marked inactive, and a disconnect log is written.

---

## Protocol flow

1. Device opens a TLS connection to `TLS_HOST:TLS_PORT` (default `0.0.0.0:6501`).
2. Device sends an HTTP-style POST whose body is a `DssProtocol` JSON document (`MSG_DEV_REGISTER_REQ`).
3. Server parses the payload, upserts the device, refreshes Redis presence, appends a `register` log.
4. Server replies with `MSG_DEV_REGISTER_RSP` (`ErrorNum: 200`) and a keep-alive interval hint.
5. If no further messages arrive within `HEARTBEAT_TIMEOUT`, the connection is closed and disconnect handling runs.

Example request body (simplified):

```json
{
  "DssProtocol": {
    "Header": {
      "CSeq": "1",
      "MessageType": "MSG_DEV_REGISTER_REQ",
      "Version": "1.0"
    },
    "Body": {
      "SerialNumber": "9344ff174b004410jsc6",
      "Area": "Europe:Netherlands:Default",
      "AuthCode": "…",
      "Enable": "1",
      "StreamLevel": "…",
      "StreamServerIPs": ["0.0.0.0"],
      "LiveStatus": ["-1", "0"],
      "UserInfo": []
    }
  }
}
```

---

## Tech stack

- **Python 3.9+** — `asyncio`, `ssl`
- **Redis** (`redis.asyncio`) — live device keys with expiration
- **MySQL** + **Tortoise ORM** / **aiomysql** — persistence
- **Loguru** — console + rotating file logging
- **OpenSSL** — self-signed certs for local TLS

---

## Features

- Asynchronous TLS server with per-client session handling
- Device registration via JSON-over-HTTP on a raw TLS socket
- Redis-backed live presence with automatic key expiry
- MySQL upsert of device metadata (`serial`, area, stream config, live status, …)
- Structured `DeviceLog` events for register / disconnect
- Configurable heartbeat timeout and Redis TTL
- Single-device test client and a clustered load-test client

---

## Getting started

### Prerequisites

- Python 3.9+
- MySQL (database + user ready)
- Redis
- OpenSSL (for generating local certificates)

### Setup

```bash
git clone https://github.com/vel0cirapt0r/dvr_server_2.git
cd dvr_server_2

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# TLS certificates (self-signed for local / lab use)
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes

# Local config (gitignored — never commit real credentials)
cp sample_config.py config.py
# Edit config.py: MYSQL_URL, Redis settings, timeouts
```

Create a MySQL database/user that match your `config.py` (default sample uses database `dvr_db`).

### Run the server

```bash
python3 main.py
```

Listens on the host/port from `config.py` (default **`0.0.0.0:6501`**).

### Single-device test

```bash
python3 test_client.py
```

Opens one TLS connection, sends a registration POST, prints the response, and holds the connection long enough to exercise timeout behavior.

### Load test

```bash
python3 clustered_test_client.py
```

Simulates a large device fleet (default: up to **20,000** client tasks, **10** registrations each, ~**118s** between sends). A semaphore caps in-flight clients at **1,000** so a single machine isn’t overwhelmed — tune `TOTAL_CLIENTS`, `REQUESTS_PER_CLIENT`, `INTERVAL_SECONDS`, and the semaphore in the script for your hardware.

> Treat load numbers as a **harness for stress testing**, not a certified benchmark. Results depend on CPU, file descriptors, Redis/MySQL capacity, and network.

---

## Configuration

Copy `sample_config.py` → `config.py` and adjust:

| Setting | Role |
|---------|------|
| `CERT_PATH` / `KEY_PATH` | TLS certificate and private key |
| `TLS_HOST` / `TLS_PORT` | Bind address (default `0.0.0.0:6501`) |
| `MYSQL_URL` | Tortoise / MySQL connection string |
| `REDIS_*` | Redis host, port, DB, optional password |
| `HEARTBEAT_TIMEOUT` | Seconds of silence before disconnect (default `120`) |
| `REDIS_KEY_EXPIRE` | Presence key TTL — keep slightly above the heartbeat window |

`config.py`, `certs/*.pem`, and `.env` are gitignored so local secrets stay local.

---

## Project structure

```text
.
├── main.py                     # Entry: init DB, start TLS server
├── tls_server.py               # asyncio TLS server + ClientSession / heartbeat
├── message_handler.py          # Parse protocol, Redis + MySQL updates, responses
├── redis_client.py             # Async Redis presence helpers
├── logger.py                   # Loguru console + rotating file sink
├── sample_config.py            # Template → copy to config.py
├── test_client.py              # One-device registration client
├── clustered_test_client.py    # Multi-device load harness
├── requirements.txt
├── db/
│   ├── init.py                 # Tortoise init + schema generation
│   └── models.py               # Device, DeviceLog
├── certs/                      # Place cert.pem / key.pem here (not committed)
└── logs/                       # server.log (rotated)
```

---

## Logging

- **Console** — structured debug/info during development
- **File** — `logs/server.log`, rotated every **100 MB**, retained **7 days**

Connection, registration, timeout, and disconnect paths are logged with peer IP / serial context where available.

---

## Design notes (interview-friendly)

- **Long-lived TLS sessions**, not short REST calls — each device keeps a socket open; idle detection is timeout-based reads, not a separate heartbeat daemon.
- **Redis TTL as a safety net** — even if a process dies mid-session, presence keys expire without manual cleanup.
- **MySQL for truth over time** — who registered, last seen, disconnect reason, raw payload for debugging field devices.
- **Thin protocol adapter** — HTTP framing is only a transport wrapper; the domain model is `DssProtocol` register/response.

---

## License

[MIT](LICENSE)
