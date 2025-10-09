from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.mongo_url)
db = client[settings.mongo_db]

# Exemple : accès à une collection 
pokemon_collection = db["pokemons"]

async def get_database(): 
    """Dépendance FastAPI pour accéder à la base
    """
    return db