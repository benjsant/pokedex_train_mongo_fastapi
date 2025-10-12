from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom Pydantic-compatible ObjectId for MongoDB models."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# --- Base Model ---
class PokemonBase(BaseModel):
    """
    Base model representing a Pokémon.
    Shared by creation and response models.
    """

    pokedex_num: int = Field(..., description="Numéro du Pokédex", example=25)
    name: str = Field(..., description="Nom du Pokémon", example="Pikachu")
    types: List[str] = Field(..., description="Types du Pokémon", example=["Électrik"])
    height: Optional[float] = Field(None, description="Taille en mètres", example=0.4)
    weight: Optional[float] = Field(None, description="Poids en kilogrammes", example=6.0)
    description: Optional[str] = Field(
        None, description="Description du Pokémon", 
        example="Pikachu stocke de l’électricité dans ses joues."
    )
    evolutions: Optional[List[str]] = Field(
        None, description="Chaîne d'évolution", example=["Raichu"]
    )

    model_config = ConfigDict(extra="ignore")


# --- Create Model ---
class PokemonCreate(PokemonBase):
    """
    Model used when creating a new Pokémon (POST).
    Does not include an ID field.
    """
    pass


# --- Response Model ---
class PokemonResponse(PokemonBase):
    """
    Model returned when fetching a Pokémon (GET).
    Includes MongoDB ObjectId as `_id`.
    """

    id: Optional[PyObjectId] = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        extra="ignore"
    )

    def to_mongo(self) -> dict:
        """Convert the model into a MongoDB-ready dictionary."""
        data = self.dict(by_alias=True, exclude_none=True)
        if "_id" in data and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        return data
