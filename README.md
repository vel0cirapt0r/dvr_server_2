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

1. **Clone the repository**

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
git clone https://github.com/vel0cirapt0r/dvr_server_2.git
cd dvr_server_2
````

**Windows (PowerShell or CMD):**

```cmd
git clone https://github.com/vel0cirapt0r/dvr_server_2.git
cd dvr_server_2
```

</details>

---

2. **Install dependencies**

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
pip3 install -r requirements.txt
```

**Windows:**

```cmd
pip install -r requirements.txt
```

</details>

---

3. **Generate TLS certificates**

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
mkdir certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
```

**Windows (PowerShell):**

```powershell
mkdir certs
openssl req -x509 -newkey rsa:4096 -keyout certs\key.pem -out certs\cert.pem -days 365 -nodes
```

</details>

---

4. **Copy the sample config**

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
cp sample_config.py config.py
```

**Windows (PowerShell or CMD):**

```cmd
copy sample_config.py config.py
```

</details>

Then edit `config.py` to set your MySQL, Redis, TLS, and timeout configurations.

---

## Usage

### Running the Server

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
python3 main.py
```

**Windows:**

```cmd
py main.py
```

</details>

The server listens on the configured TLS host and port (default `0.0.0.0:6501`).

---

### Testing with Single Client

Use `test_client.py` to simulate a single device registering:

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
python3 test_client.py
```

**Windows:**

```cmd
py test_client.py
```

</details>

---

### Clustered Load Testing

Use `clustered_test_client.py` to simulate 20,000 concurrent devices sending registration requests 10 times each with a 118-second interval.

<details>
<summary>Show commands for Linux/macOS/Windows</summary>

**Linux/macOS:**

```bash
python3 clustered_test_client.py
```

**Windows:**

```cmd
py clustered_test_client.py
```

</details>

> ⚠️ Note: The clustered test client limits concurrency to 1000 clients at once to avoid overwhelming your machine. Adjust as needed.

---

Here’s the updated **Project Structure** section for your `README.md`, with a detailed tree view of your repository layout:

---

## Project Structure

```
.
├── LICENSE
├── README.md
├── clustered_test_client.py        # Load testing client simulating 20,000+ connections
├── config.py                       # Your actual runtime configuration
├── db
│   ├── init.py
│   └── models.py                   # Device and log models using Tortoise ORM
├── logger.py                       # Logging setup for console and file output
├── main.py                         # Entry point that runs the TLS server
├── message_handler.py              # Processes incoming messages and updates state
├── redis_client.py                 # Redis helper functions (asyncio-based)
├── requirements.txt                # Python dependencies
├── sample_config.py                # Template config to copy as `config.py`
├── test_client.py                  # Simple single-device client for testing
└── tls_server.py                   # Core TLS server logic using asyncio and ssl
```


---

## Configuration

All settings are loaded from `config.py`.
You should create this file by copying `sample_config.py` and editing it with your own credentials and paths.

---

## Logging

Logs are output to the console and saved to:

```
logs/server.log
```

Rotated every 100MB, retained for 7 days.

---

## License

MIT License

```
