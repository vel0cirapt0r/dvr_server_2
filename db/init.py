from tortoise import Tortoise

from config import MYSQL_URL


async def init_db():
    await Tortoise.init(
        db_url=MYSQL_URL,
        modules={"models": ["db.models"]},
    )
    await Tortoise.generate_schemas()
