import redis.asyncio as redis

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_KEY_EXPIRE

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)


async def update_device_in_redis(serial_number, ip, raw_data):
    key = f"device:{serial_number}"
    await redis_client.hset(key, mapping={
        "last_seen": str(raw_data["DssProtocol"]["Header"]["CSeq"]),
        "raw": str(raw_data),
        "ip": ip
    })
    await redis_client.expire(key, REDIS_KEY_EXPIRE)

async def delete_device_from_redis(serial_number):
    await redis_client.delete(f"device:{serial_number}")
