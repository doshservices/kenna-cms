from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from beanie import init_beanie


load_dotenv()
import os

from .logger import logger


async def connect_to_database():
    from ..modules import User, Book, News, Insight, InsightAuthor

    try:
        client = AsyncIOMotorClient(os.getenv("DATABASE_URI"))
        await init_beanie(
            database=client.Kennapatner, document_models=[User, Book, News, Insight, InsightAuthor]
        )
        logger.info("Database connected")

    except PyMongoError as e:
        logger.error(e)
        raise

    except Exception as e:
        logger.error(e)
        raise
