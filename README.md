# TLS Device Server

A scalable and asynchronous TLS server built in Python to handle device registration and communication over secure connections. Designed to support 10,000+ concurrent clients with heartbeat timeout and real-time device state management.

---

## Features

* **Asynchronous TLS Server:** Built with Python `asyncio` and `ssl` for efficient handling of thousands of concurrent clients.
* **Device Registration & Management:** Devices register via JSON-over-HTTP POST messages over TLS.
* **Redis Integration:** Real-time device status and heartbeat info stored in Redis with automatic expiration.
* **MySQL Persistence:** Device details and logs stored in MySQL for long-term record keeping.
* **Heartbeat Timeout:** Disconnects devices after a configurable timeout period of inactivity.
* **Structured Logging:** Logs device events, connections, and disconnections with detailed metadata.
* **Clustered Test Client:** Simulates 20,000 concurrent devices sending repeated registration requests to stress test the server.

---

## Getting Started

### Prerequisites

* Python 3.9+
* MySQL server (with database and user configured)
* Redis server
* OpenSSL for generating certificates

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/vel0cirapt0r/dvr_server_2.git
   cd dvr_server_2
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate TLS certificates (or use your own):

   ```bash
   mkdir certs
   openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
   ```

4. Copy the sample config and customize your settings:

   ```bash
   cp sample_config.py config.py
   ```

   Then edit `config.py` to set your MySQL, Redis, TLS, and timeout configurations.

---

## Usage

### Running the Server

```bash
python main.py
```

The server listens on the configured TLS host and port (default `0.0.0.0:6501`).

### Testing with Single Client

Use `test_client.py` to simulate a single device registering:

```bash
python test_client.py
```

### Clustered Load Testing

Use `clustered_test_client.py` to simulate 20,000 concurrent devices sending registration requests 10 times each with a 118-second interval:

```bash
python clustered_test_client.py
```

**Note:** The clustered test client limits concurrency to 1000 clients at once to avoid overwhelming your machine. Adjust as needed.

---

## Project Structure

* `tls_server.py` — Main TLS server handling device connections.
* `message_handler.py` — Processes incoming device messages and manages DB/Redis updates.
* `redis_client.py` — Async Redis helper functions for device state management.
* `db/models.py` — Database models for devices and logs using Tortoise ORM.
* `test_client.py` — Simple TLS client for manual testing.
* `clustered_test_client.py` — Load testing client simulating massive concurrent connections.
* `logger.py` — Configured logging with console and file output.
* `sample_config.py` — Sample config file to copy and customize.

---

## Configuration

All settings are loaded from `config.py`. You should create this file by copying `sample_config.py` and editing it with your own credentials and paths.

---

## Logging

Logs are output to console and saved in `logs/server.log`, rotated every 100MB and retained for 7 days.

---

## License

MIT License

