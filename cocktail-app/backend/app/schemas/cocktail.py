from pydantic import BaseModel
from typing import List, Optional

class CocktailBase(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    image: str

class CocktailCreate(CocktailBase):
    pass

class CocktailUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    image: Optional[str] = None

class Cocktail(CocktailBase):
    id: int

    class Config:
        from_attributes = True
