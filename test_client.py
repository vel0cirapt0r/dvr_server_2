import asyncio
import ssl
import json

from logger import logger

MESSAGE = {
    "DssProtocol": {
        "Header": {
            "CSeq": "1",
            "MessageType": "MSG_DEV_REGISTER_REQ",
            "Version": "1.0"
        },
        "Body": {
            "SerialNumber": "9344ff174b004410jsc6",
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

async def main():
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    reader, writer = await asyncio.open_connection('127.0.0.1', 6501, ssl=ssl_context)

    logger.info("[*] Connected to TLS server")

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

    # Read server response until EOF (connection closed)
    while True:
        data = await reader.read(8192)
        if not data:
            logger.info("[*] Server closed the connection")
            break
        logger.info("[*] Server response chunk:")
        logger.info(data.decode())

    response = await reader.read(8192)
    logger.info("[*] Server response:")
    logger.info(response.decode())

    logger.info("[*] Keeping connection alive for 130 seconds to test timeout...")
    await asyncio.sleep(130)

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
