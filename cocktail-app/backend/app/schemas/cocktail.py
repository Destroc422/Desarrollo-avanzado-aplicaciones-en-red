from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class IngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    unit: str = Field(min_length=1, max_length=20)
    unit_cost_cop: int = Field(ge=0, le=100000000)


class CocktailFields(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=2, max_length=2000)
    category: str = Field(min_length=2, max_length=80)
    price_cop: int = Field(ge=1, le=100000000)
    ingredients: list[IngredientInput] = Field(min_length=1, max_length=40)
    instructions: str = Field(default="", max_length=4000)
    image: str = Field(default="", max_length=500)
    is_available: bool = True


class CocktailCreate(CocktailFields):
    pass


class CocktailUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, min_length=2, max_length=2000)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    price_cop: int | None = Field(default=None, ge=1, le=100000000)
    ingredients: list[IngredientInput] | None = Field(default=None, min_length=1, max_length=40)
    instructions: str | None = Field(default=None, max_length=4000)
    image: str | None = Field(default=None, max_length=500)
    is_available: bool | None = None


class CocktailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    category: str
    price_cop: int
    estimated_cost_cop: int
    ingredients: list[IngredientInput]
    instructions: str
    image: str
    is_available: bool


class CocktailPage(BaseModel):
    items: list[CocktailRead]
    total: int
    page: int
    page_size: int
