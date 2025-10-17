from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.pokemon import PokemonCreate, PokemonResponse
from app.services import pokemon_service

router = APIRouter(prefix="/pokemons", tags=["Pokemons"])


# --- CRUD ---
@router.post("/", response_model=PokemonResponse)
async def create_pokemon(pokemon: PokemonCreate):
    return await pokemon_service.create_pokemon(pokemon)


@router.get("/", response_model=List[PokemonResponse])
async def list_pokemons(limit: int = 50, skip: int = 0):
    return await pokemon_service.get_all_pokemons(limit, skip)

@router.get("/pokedex/{pokedex_id}", response_model=PokemonResponse)
async def get_pokemon(pokedex_id: int):
    pokemon = await pokemon_service.get_pokemon_by_pokedex_id(pokedex_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon introuvable")
    return pokemon

@router.get("/{pokemon_id}", response_model=PokemonResponse)
async def get_pokemon(pokemon_id: str):
    pokemon = await pokemon_service.get_pokemon_by_id(pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon introuvable")
    return pokemon


@router.put("/{pokemon_id}", response_model=PokemonResponse)
async def update_pokemon(pokemon_id: str, data: dict):
    updated = await pokemon_service.update_pokemon(pokemon_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Pokémon introuvable")
    return updated


@router.delete("/{pokemon_id}")
async def delete_pokemon(pokemon_id: str):
    deleted = await pokemon_service.delete_pokemon(pokemon_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pokémon introuvable")
    return {"status": "deleted"}


# --- FILTERS ---
@router.get("/type/{type_name}", response_model=List[PokemonResponse])
async def get_pokemons_by_type(type_name: str):
    return await pokemon_service.get_pokemons_by_type(type_name)


@router.get("/stats/{stat}", response_model=List[PokemonResponse])
async def filter_by_stat(stat: str, operator: str = Query(...), value: int = Query(...)):
    return await pokemon_service.get_pokemons_with_stat_comparison(stat, operator, value)


# --- LOGICAL OPERATORS ---
@router.post("/filters/and", response_model=List[PokemonResponse])
async def filter_with_and(filters: List[dict]):
    return await pokemon_service.get_pokemons_with_and(filters)


@router.post("/filters/or", response_model=List[PokemonResponse])
async def filter_with_or(filters: List[dict]):
    return await pokemon_service.get_pokemons_with_or(filters)


# --- AGGREGATIONS ---
@router.get("/aggregations/average/{stat}")
async def average_stat(stat: str):
    avg = await pokemon_service.get_average_stat(stat)
    return {"stat": stat, "average": avg}


@router.get("/aggregations/types")
async def type_distribution():
    return await pokemon_service.count_by_type()
