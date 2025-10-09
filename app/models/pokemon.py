from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    """Class to generate MongoDB ObjectId with Pydantic

    Args:
        ObjectId (_type_): _description_
    """
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

class Pokemon(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    pokedex_num: int= Field(...,description="Numéro du Pokedex", example=25)
    name: str = Field(...,description="Nom du Pokémon", example="Pikachu")
    types: List[str] = Field(..., example=["Électrik"])
    height: Optional[float] = Field(None, example=0.4)
    weight: Optional[float] = Field(None, example=6.0)
    description: Optional[str] = Field(None, example="Pikachu stocke de l’électricité dans ses joues.")
    evolutions: Optional[List[str]] = Field(None, example=["Raichu"])

    model_config = {
        "extra":"ignore", # ignore les champs non définis dans le modèle
        "populate_by_name":True,
        "json_encoders": {ObjectId: str}  # pour renvoyer l'ObjectId sous forme de string
    }