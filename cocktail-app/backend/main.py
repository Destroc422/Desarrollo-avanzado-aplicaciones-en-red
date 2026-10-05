from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Cocktail(BaseModel):
    id: int
    name: str
    description: str
    ingredients: List[str]
    image: str

cocktails_db = [
    {
        "id": 1,
        "name": "Margarita",
        "description": "A classic Mexican cocktail with tequila, lime, and orange liqueur.",
        "ingredients": ["Tequila", "Lime Juice", "Cointreau", "Salt"],
        "image": "https://images.unsplash.com/photo-1556679343-66655a887a74?w=500"
    },
    {
        "id": 2,
        "name": "Mojito",
        "description": "Refreshing Cuban cocktail with mint, lime, and rum.",
        "ingredients": ["White Rum", "Sugar", "Lime Juice", "Mint Leaves", "Soda Water"],
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf7596ed73?w=500"
    },
    {
        "id": 3,
        "name": "Old Fashioned",
        "description": "Timeless cocktail with bourbon, bitters, and sugar.",
        "ingredients": ["Bourbon", "Angostura Bitters", "Sugar Cube", "Orange Peel"],
        "image": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d17?w=500"
    },
    {
        "id": 4,
        "name": "Espresso Martini",
        "description": "Sophisticated blend of coffee and vodka.",
        "ingredients": ["Vodka", "Espresso", "Coffee Liqueur", "Simple Syrup"],
        "image": "https://images.unsplash.com/photo-1545436773-85d369a4597e?w=500"
    }
]

@app.get("/cocktails", response_model=List[Cocktail])
async def get_cocktails():
    return cocktails_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
