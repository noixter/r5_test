import os

from motor import motor_asyncio
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
MONGO_INITDB_ROOT_USERNAME = os.getenv("DB_USER")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("DB_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("DB_NAME", "test")
if not MONGO_URI:
    MONGO_URI = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"


@asynccontextmanager
async def mongo_client(collection: str, db_name: str = MONGO_DB):
    client = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    try:
        db = client[db_name]
        collection = db[collection]
        await collection.create_index('id', unique=True)
        yield collection
    finally:
        client.close()
