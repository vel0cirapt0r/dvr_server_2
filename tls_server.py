import asyncio
import ssl

from config import HEARTBEAT_TIMEOUT, TLS_HOST, TLS_PORT, CERT_PATH, KEY_PATH
from logger import logger
from message_handler import process_message, handle_disconnect


class ClientSession:
    def __init__(self, reader, writer, timeout):
        self.reader = reader
        self.writer = writer
        self.timeout = timeout
        self.peer_ip = writer.get_extra_info("peername")[0]
        self.serial_number = None
        self.last_msg = asyncio.get_event_loop().time()

    async def handle(self):
        try:
            logger.info(f"Connection established with {self.peer_ip}")
            while True:
                now = asyncio.get_event_loop().time()
                time_left = self.timeout - (now - self.last_msg)
                if time_left <= 0:
                    logger.warning(f"Client {self.peer_ip} timed out after {self.timeout} seconds")
                    break

                try:
                    data = await asyncio.wait_for(self.reader.read(8192), timeout=time_left)
                    if not data:
                        logger.info(f"Client {self.peer_ip} closed connection")
                        break

                    self.last_msg = asyncio.get_event_loop().time()
                    text = data.decode()
                    # logger.debug(f"Received: {text}")
                    response, serial = await process_message(text, self.peer_ip)

                    if serial:
                        self.serial_number = serial
                    if response:
                        self.writer.write(response.encode())
                        await self.writer.drain()

                except asyncio.TimeoutError:
                    logger.warning(f"Client {self.peer_ip} timed out after {self.timeout} seconds")
                    break

        except Exception as e:
            logger.error(f"Exception: {e}")
        finally:
            if self.serial_number:
                await handle_disconnect(self.serial_number)
            self.writer.close()
            await self.writer.wait_closed()
            logger.info(f"Connection closed with {self.peer_ip}")


async def start_tls_server():
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(CERT_PATH, KEY_PATH)

    server = await asyncio.start_server(
        lambda r, w: ClientSession(r, w, HEARTBEAT_TIMEOUT).handle(),
        TLS_HOST,
        TLS_PORT,
        ssl=ssl_ctx
    )

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f"TLS server started on {addrs}")

    async with server:
        await server.serve_forever()
