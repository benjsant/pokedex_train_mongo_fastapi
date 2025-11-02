from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Création du client MongoDB asynchrone
client = AsyncIOMotorClient(settings.mongo_url)

# Sélection de la base et de la collection
db = client[settings.mongo_db]
pokemon_collection = db["pokemons"]