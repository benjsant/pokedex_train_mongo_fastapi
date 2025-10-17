from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.pydantic_objectid import PyObjectId


# --- Pokémon Stats ---
class Stats(BaseModel):
    hp: Optional[int] = Field(None, description="Points de vie (HP)", example=45)
    attack: Optional[int] = Field(None, description="Attaque", example=49)
    defense: Optional[int] = Field(None, description="Défense", example=49)
    special_attack: Optional[int] = Field(None, description="Attaque spéciale", example=65, alias="special-attack")
    special_defense: Optional[int] = Field(None, description="Défense spéciale", example=65, alias="special-defense")
    speed: Optional[int] = Field(None, description="Vitesse", example=45)

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# --- Base Model ---
class PokemonBase(BaseModel):
    pokedex_id: int = Field(..., description="Numéro officiel du Pokédex", example=1)
    name: str = Field(..., description="Nom du Pokémon (anglais)")
    name_fr: Optional[str] = Field(None, description="Nom du Pokémon (français)")
    types: List[str] = Field(..., description="Types du Pokémon")
    height_m: Optional[float] = Field(None, description="Taille en mètres")
    weight_kg: Optional[float] = Field(None, description="Poids en kilogrammes")
    stats: Optional[Stats] = Field(None, description="Statistiques du Pokémon")
    description_fr: Optional[str] = Field(None, description="Description en français")
    evolution_chain_url: Optional[str] = Field(None, description="URL de la chaîne d'évolution")
    evolves_from: Optional[str] = Field(None, description="Pokémon dont il évolue")

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# --- Create Model ---
class PokemonCreate(PokemonBase):
    pass


# --- Response Model ---
class PokemonResponse(PokemonBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        extra="ignore"
    )

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        return data
