from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
