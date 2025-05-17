from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/server.log", rotation="100 MB", retention="7 days", level="DEBUG")
