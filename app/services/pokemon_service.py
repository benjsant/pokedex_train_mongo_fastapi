from app.db.connection import db

# CREATE 
async def create_pokemon(pokemon_data: dict):
    """Add a pokemon if it doesn't exist already

    Args:
        pokemon_data (dict): _description_
    """
    exists = await db["pokemon"].find_one({"id": pokemon_data["id"]})
    if exists: 
        return None
    await db["pokemon"].insert_one(pokemon_data)
    return pokemon_data

# READ 
async def get_pokemon_by_id(pokemon_id: int):
    return await db["pokemon"].find_one({"id": pokemon_id}, {"_id": 0})

async def get_all_pokemons(limit: int = 151):
    cursor = db["pokemon"].find({},{"_id":0}).limit(limit)
    return await cursor.to_list(length=limit)

async def get_pokemons_by_type(poke_type: str):
    cursor = db["pokemon"].find({"types": poke_type}, {"_id":0})
    return await cursor.to_list(length=100)

# UPDATE 
async def update_pokemon(pokemon_id: int, update_data: dict):
    result = await db["pokemon"].update_one(
        {"id": pokemon_id},
        {"$set": update_data}
    )
    return result.modified_count # 1 if modification, 0 if it doesn't 

# DELETE 
async def delete_pokemon(pokemon_id: int):
    result = await db["pokemon"].delete_one({"id": pokemon_id})
    return result.deleted_count # 1 if deleted, 0 if it doesn't 

# INDEX (For faster reseach by type)
async def create_index():
    """Create an index for the placeholder 'types' """
    await db["pokemon"].create_index("types")