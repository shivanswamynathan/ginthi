
import os
import motor.motor_asyncio
from beanie import init_beanie
from dotenv import load_dotenv
import inspect
import app.schemas as schemas
from beanie import Document

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Collect all Beanie Document subclasses
document_models = [
    cls for name, cls in inspect.getmembers(schemas)
    if inspect.isclass(cls) and issubclass(cls, Document)
]

print(
    f"Document models found: {[model.__name__ for model in document_models]}")


async def init_db():
    await init_beanie(database=db, document_models=document_models)
    return db


async def get_db():
    return db
