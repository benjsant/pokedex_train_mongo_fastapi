from typing import List, Optional
from bson import ObjectId
from app.models.pokemon import PokemonCreate, PokemonResponse
from app.core.database import pokemon_collection
from pymongo import ASCENDING


# --- CREATE ---
async def create_pokemon(pokemon: PokemonCreate) -> PokemonResponse:
    pokemon_dict = pokemon.model_dump(by_alias=True, exclude_none=True)
    result = await pokemon_collection.insert_one(pokemon_dict)
    created_pokemon = await pokemon_collection.find_one({"_id": result.inserted_id})
    if created_pokemon:
        created_pokemon["_id"] = str(created_pokemon["_id"])
    return PokemonResponse(**created_pokemon)


# --- READ ---
async def get_all_pokemons(limit: int = 50, skip: int = 0) -> List[PokemonResponse]:
    cursor = pokemon_collection.find().skip(skip).limit(limit)
    pokemons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pokemons.append(PokemonResponse(**doc))
    return pokemons


async def get_pokemon_by_id(pokemon_id: str) -> Optional[PokemonResponse]:
    if not ObjectId.is_valid(pokemon_id):
        return None
    doc = await pokemon_collection.find_one({"_id": ObjectId(pokemon_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
        return PokemonResponse(**doc)
    return None

async def get_pokemon_by_pokedex_id(pokedex_id: int) -> Optional[PokemonResponse]:
    doc = await pokemon_collection.find_one({"pokedex_id": pokedex_id})
    if doc:
        doc["_id"] = str(doc["_id"])
        return PokemonResponse(**doc)
    return None

async def get_pokemon_by_name(name: str) -> Optional[PokemonResponse]:
    doc = await pokemon_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if doc:
        doc["_id"] = str(doc["_id"])
        return PokemonResponse(**doc)
    return None


# --- UPDATE ---
async def update_pokemon(pokemon_id: str, data: dict) -> Optional[PokemonResponse]:
    if not ObjectId.is_valid(pokemon_id):
        return None
    await pokemon_collection.update_one({"_id": ObjectId(pokemon_id)}, {"$set": data})
    updated = await pokemon_collection.find_one({"_id": ObjectId(pokemon_id)})
    if updated:
        updated["_id"] = str(updated["_id"])
        return PokemonResponse(**updated)
    return None


# --- DELETE ---
async def delete_pokemon(pokemon_id: str) -> bool:
    if not ObjectId.is_valid(pokemon_id):
        return False
    result = await pokemon_collection.delete_one({"_id": ObjectId(pokemon_id)})
    return result.deleted_count > 0


# --- FILTERS / COMPARATORS ---
async def get_pokemons_by_type(type_name: str) -> List[PokemonResponse]:
    cursor = pokemon_collection.find({"types": {"$in": [type_name]}})
    pokemons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pokemons.append(PokemonResponse(**doc))
    return pokemons


async def get_pokemons_with_stat_comparison(stat: str, operator: str, value: int) -> List[PokemonResponse]:
    operators = {
        "gt": "$gt",
        "gte": "$gte",
        "lt": "$lt",
        "lte": "$lte",
        "eq": "$eq",
    }
    if operator not in operators:
        raise ValueError("Invalid operator")

    query = {f"stats.{stat}": {operators[operator]: value}}
    cursor = pokemon_collection.find(query)
    pokemons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pokemons.append(PokemonResponse(**doc))
    return pokemons


# --- LOGICAL OPERATORS ---
async def get_pokemons_with_and(filters: List[dict]) -> List[PokemonResponse]:
    cursor = pokemon_collection.find({"$and": filters})
    pokemons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pokemons.append(PokemonResponse(**doc))
    return pokemons


async def get_pokemons_with_or(filters: List[dict]) -> List[PokemonResponse]:
    cursor = pokemon_collection.find({"$or": filters})
    pokemons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pokemons.append(PokemonResponse(**doc))
    return pokemons


# --- AGGREGATION EXAMPLES ---
async def get_average_stat(stat: str) -> float:
    pipeline = [
        {"$match": {f"stats.{stat}": {"$exists": True}}},
        {"$group": {"_id": None, "avg_value": {"$avg": f"$stats.{stat}"}}},
    ]
    result = await pokemon_collection.aggregate(pipeline).to_list(length=1)
    return result[0]["avg_value"] if result else 0.0


async def count_by_type() -> List[dict]:
    pipeline = [
        {"$unwind": "$types"},
        {"$group": {"_id": "$types", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return await pokemon_collection.aggregate(pipeline).to_list(length=None)


# --- INDEXES ---
async def create_indexes():
    """Crée des index pour améliorer les performances, compatible MongoDB 6+."""
    try:
        # 1️⃣ Index unique sur le nom
        await pokemon_collection.create_index([("name", ASCENDING)], unique=True)

        # 2️⃣ Index unique sur pokedex_id
        # On remplace les valeurs null ou manquantes par 0 avant de créer l'index
        await pokemon_collection.update_many({"pokedex_id": {"$exists": False}}, {"$set": {"pokedex_id": 0}})
        await pokemon_collection.update_many({"pokedex_id": None}, {"$set": {"pokedex_id": 0}})
        await pokemon_collection.create_index([("pokedex_id", ASCENDING)], unique=True)

        # 3️⃣ Index sur types pour filtrages rapides
        await pokemon_collection.create_index([("types", ASCENDING)])

        print("✅ Index MongoDB créés avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des index : {e}")
