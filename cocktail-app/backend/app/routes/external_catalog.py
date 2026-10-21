import json
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Query


router = APIRouter(prefix="/external-catalog", tags=["external-catalog"])
COCKTAIL_DB = "https://www.thecocktaildb.com/api/json/v1/1/"


def _fetch(endpoint: str, params: dict[str, str]):
    url = COCKTAIL_DB + endpoint + "?" + urlencode(params)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "ElGrilloCocktailApp/1.0"})
    try:
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read(2 * 1024 * 1024).decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        raise HTTPException(status_code=502, detail="El catálogo externo no está disponible en este momento.")


@router.get("/recipes")
def search_recipes(
    search: str = Query(default="", max_length=100),
    category: str | None = Query(default=None, max_length=80),
    recipe_id: str | None = Query(default=None, max_length=20),
):
    if recipe_id:
        if not recipe_id.isdigit():
            raise HTTPException(status_code=422, detail="El identificador de la receta no es válido.")
        result = _fetch("lookup.php", {"i": recipe_id})
    elif search.strip():
        result = _fetch("search.php", {"s": search.strip()})
    elif category and category.strip():
        result = _fetch("filter.php", {"c": category.strip()})
    else:
        raise HTTPException(status_code=422, detail="Escribe un nombre o selecciona una categoría.")
    return {"items": result.get("drinks") or []}
