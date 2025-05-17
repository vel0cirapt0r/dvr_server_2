import asyncio
from logger import logger
from db.init import init_db
from tls_server import start_tls_server

async def main():
    await init_db()
    await start_tls_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Server shut down by user.")
