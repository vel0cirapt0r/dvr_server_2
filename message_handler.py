import json
from datetime import datetime
from logger import logger
from redis_client import update_device_in_redis, delete_device_from_redis
from db.models import Device, DeviceLog

def extract_json_from_http(data):
    try:
        if isinstance(data, bytes):
            text = data.decode()
        elif isinstance(data, str):
            text = data
        else:
            raise TypeError(f"Unexpected data type: {type(data)}")

        _, _, body = text.partition("\r\n\r\n")
        if not body:
            _, _, body = text.partition("\n\n")

        return json.loads(body)
    except Exception as e:
        logger.error(f"Failed to extract JSON: {e}")
        raise

async def process_message(data: str, peer_ip: str):
    try:
        message = extract_json_from_http(data)
        header = message["DssProtocol"]["Header"]
        body = message["DssProtocol"]["Body"]
        serial = body["SerialNumber"]

        # Redis update
        await update_device_in_redis(serial, peer_ip, message)

        # MySQL upsert
        device, created = await Device.get_or_create(
            serial_number=serial,
            defaults={
                "area": body.get("Area"),
                "auth_code": body.get("AuthCode"),
                "enable": body.get("Enable"),
                "stream_level": body.get("StreamLevel"),
                "stream_server_ips": body.get("StreamServerIPs"),
                "user_info": body.get("UserInfo"),
                "live_status": body.get("LiveStatus"),
                "rewrite_oem_id": body.get("RewriteOemID"),
                "last_seen": datetime.utcnow(),
                "is_active": True,
                "json_raw": json.dumps(message),
            }
        )

        if not created:
            device.area = body.get("Area")
            device.auth_code = body.get("AuthCode")
            device.enable = body.get("Enable")
            device.stream_level = body.get("StreamLevel")
            device.stream_server_ips = body.get("StreamServerIPs")
            device.user_info = body.get("UserInfo")
            device.live_status = body.get("LiveStatus")
            device.rewrite_oem_id = body.get("RewriteOemID")
            device.last_seen = datetime.utcnow()
            device.is_active = True
            device.json_raw = json.dumps(message)
            await device.save()


        # Structured log creation
        await DeviceLog.create(
            device=device,
            event_type="register",
            ip_address=peer_ip,
            json_raw=message,
            details=f"Device {serial} registered from IP {peer_ip}",
            extra_info={
                "area": body.get("Area"),
                "stream_level": body.get("StreamLevel"),
                "auth_code": body.get("AuthCode"),
                "user_info": body.get("UserInfo"),
                "live_status": body.get("LiveStatus"),
            }
        )

        response = {
            "DssProtocol": {
                "Header": {
                    "CSeq": header["CSeq"],
                    "MessageType": "MSG_DEV_REGISTER_RSP",
                    "ErrorNum": "200",
                    "ErrorString": "Success Ok",
                    "Version": header["Version"]
                },
                "Body": {
                    "KeepAliveIntervel": "120"
                }
            }
        }

        return json.dumps(response), serial

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return None, None

async def handle_disconnect(serial):
    try:
        await delete_device_from_redis(serial)
        device = await Device.get(serial_number=serial)
        device.disconnected_at = datetime.utcnow()
        device.is_active = False
        await device.save()

        await DeviceLog.create(
            device=device,
            event_type="disconnect",
            ip_address=None,
            details=f"Device {serial} disconnected after timeout.",
            extra_info={"disconnected_reason": "timeout"}
        )

    except Exception as e:
        logger.error(f"Error during disconnect handling: {e}")
