from fastapi import APIRouter, HTTPException
from app.models.pokemon import Pokemon
from app.services.pokemon_service import(
    create_pokemon,
    get_pokemon_by_id,
    get_all_pokemons,
    get_pokemons_by_type,
    update_pokemon,
    delete_pokemon,
    create_index
)

router = APIRouter(prefix="/pokemon",tags=["Pokémon"])

@router.post("/", response_model=Pokemon)
async def add_pokemon(pokemon: Pokemon):
    created = await create_pokemon(pokemon.dict())