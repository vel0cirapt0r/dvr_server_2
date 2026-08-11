import os
from urllib.parse import quote_plus

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CERT_PATH = os.path.join(BASE_DIR, "certs", "cert.pem")
KEY_PATH = os.path.join(BASE_DIR, "certs", "key.pem")
TLS_PORT = 6501
TLS_HOST = "0.0.0.0"

MYSQL_PASSWORD = quote_plus("pass")
MYSQL_URL = f"mysql://user:{MYSQL_PASSWORD}@localhost:3306/dvr_db"

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

HEARTBEAT_TIMEOUT = 120
REDIS_KEY_EXPIRE = 180
