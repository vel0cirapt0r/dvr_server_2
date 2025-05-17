import asyncio
import ssl
import json
from logger import logger

TOTAL_CLIENTS = 20000
REQUESTS_PER_CLIENT = 10
INTERVAL_SECONDS = 118

MESSAGE = {
    "DssProtocol": {
        "Header": {
            "CSeq": "1",
            "MessageType": "MSG_DEV_REGISTER_REQ",
            "Version": "1.0"
        },
        "Body": {
            "SerialNumber": "test-serial-{client_id}",
            "Area": "Europe:Netherlands:Default",
            "AuthCode": "9344ff174b004410jsc6",
            "Enable": "1",
            "LiveStatus": ["-1", "0", "-1", "0", "-1", "0", "-1", "0"],
            "RewriteOemID": "General",
            "StreamLevel": "0_3:1_1_0:2_3:3_1_0:4_3:5_1_0:6_3:7_1_0",
            "StreamServerIPs": ["0.0.0.0"] * 8,
            "UserInfo": [{
                "InfoAuth": "01_02_03_04",
                "InfoPwd": "HJvh3M32tSgqsXn4rXRZhQ==",
                "InfoUsr": "aOpEe8010+njyN4RfQYq1g=="
            }]
        }
    }
}

async def run_client(client_id: int):
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    serial = f"test-serial-{client_id}"
    # Update serial in message
    MESSAGE["DssProtocol"]["Body"]["SerialNumber"] = serial

    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 6501, ssl=ssl_context)
        logger.info(f"Client {client_id} connected")

        for i in range(REQUESTS_PER_CLIENT):
            MESSAGE["DssProtocol"]["Header"]["CSeq"] = str(i+1)
            json_data = json.dumps(MESSAGE)
            http_payload = (
                f"POST / HTTP/1.1\r\n"
                f"Host: 127.0.0.1\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(json_data)}\r\n"
                f"\r\n"
                f"{json_data}"
            )

            writer.write(http_payload.encode('utf-8'))
            await writer.drain()
            logger.info(f"Client {client_id} sent request {i+1}")

            # Optionally read response here, or just fire-and-forget
            data = await reader.read(8192)
            if data:
                logger.info(f"Client {client_id} received response: {data.decode(errors='ignore')}")
            else:
                logger.warning(f"Client {client_id} connection closed by server early.")
                break

            if i < REQUESTS_PER_CLIENT - 1:
                await asyncio.sleep(INTERVAL_SECONDS)

        writer.close()
        await writer.wait_closed()
        logger.info(f"Client {client_id} connection closed")

    except Exception as e:
        logger.error(f"Client {client_id} exception: {e}")


async def main():
    logger.info(f"Starting {TOTAL_CLIENTS} clients")
    semaphore = asyncio.Semaphore(1000)  # Limit concurrency to 1000 clients at once to avoid overload

    async def sem_run(client_id):
        async with semaphore:
            await run_client(client_id)

    tasks = [asyncio.create_task(sem_run(i)) for i in range(TOTAL_CLIENTS)]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
