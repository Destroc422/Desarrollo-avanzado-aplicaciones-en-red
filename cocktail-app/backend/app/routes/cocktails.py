import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import require_staff
from ..core.config import UPLOAD_DIR
from ..database.session import get_db
from ..models.cocktail import CocktailModel
from ..models.user import UserModel
from ..schemas.cocktail import (
    CocktailCreate,
    CocktailPage,
    CocktailRead,
    CocktailUpdate,
    IngredientInput,
)


router = APIRouter(prefix="/cocktails", tags=["catalog"])


def _ingredients_from_storage(value: str | None) -> list[IngredientInput]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [IngredientInput.model_validate(item) for item in parsed]
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    # Convert legacy comma-separated records without discarding their names.
    return [
        IngredientInput(name=name.strip(), quantity=Decimal("1"), unit="unidad", unit_cost_cop=0)
        for name in value.split(",")
        if name.strip()
    ]


def _estimated_cost(ingredients: list[IngredientInput]) -> int:
    total = sum((item.quantity * item.unit_cost_cop for item in ingredients), Decimal("0"))
    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _serialize(row: CocktailModel) -> CocktailRead:
    return CocktailRead(
        id=row.id,
        name=row.name,
        description=row.description or "",
        category=row.category or "Cócteles",
        price_cop=row.price_cop or 0,
        estimated_cost_cop=row.estimated_cost_cop or 0,
        ingredients=_ingredients_from_storage(row.ingredients),
        instructions=row.instructions or "",
        image=row.image or "",
        is_available=bool(row.is_available),
    )


def _apply_payload(row: CocktailModel, values: dict) -> None:
    ingredients = values.pop("ingredients", None)
    if ingredients is not None:
        serialized = [item.model_dump(mode="json") for item in ingredients]
        row.ingredients = json.dumps(serialized, ensure_ascii=False)
        row.estimated_cost_cop = _estimated_cost(ingredients)
    for key, value in values.items():
        setattr(row, key, value)


@router.get("", response_model=CocktailPage)
def read_catalog(
    search: str = Query(default="", max_length=120),
    category: Optional[str] = Query(default=None, max_length=80),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(CocktailModel).filter(CocktailModel.is_available.is_(True))
    if search.strip():
        query = query.filter(func.lower(CocktailModel.name).contains(search.strip().lower()))
    if category and category.strip():
        query = query.filter(CocktailModel.category == category.strip())
    total = query.count()
    rows = (
        query.order_by(CocktailModel.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return CocktailPage(items=[_serialize(row) for row in rows], total=total, page=page, page_size=page_size)


@router.get("/categories", response_model=list[str])
def read_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(CocktailModel.category)
        .filter(CocktailModel.is_available.is_(True))
        .distinct()
        .order_by(CocktailModel.category.asc())
        .all()
    )
    return [row[0] for row in rows if row[0]]


@router.get("/admin", response_model=list[CocktailRead])
def read_admin_catalog(
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    rows = db.query(CocktailModel).order_by(CocktailModel.name.asc()).all()
    return [_serialize(row) for row in rows]


@router.get("/{cocktail_id}", response_model=CocktailRead)
def read_cocktail(cocktail_id: int, db: Session = Depends(get_db)):
    row = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if not row or not row.is_available:
        raise HTTPException(status_code=404, detail="El producto no está disponible.")
    return _serialize(row)


@router.post("", response_model=CocktailRead, status_code=status.HTTP_201_CREATED)
def create_cocktail(
    payload: CocktailCreate,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = CocktailModel(
        name=payload.name.strip(),
        description=payload.description.strip(),
        category=payload.category.strip(),
        price_cop=payload.price_cop,
        image=payload.image,
        instructions=payload.instructions.strip(),
        is_available=payload.is_available,
        ingredients="[]",
        estimated_cost_cop=0,
    )
    _apply_payload(row, payload.model_dump(exclude={"ingredients"}))
    _apply_payload(row, {"ingredients": payload.ingredients})
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.put("/{cocktail_id}", response_model=CocktailRead)
def update_cocktail(
    cocktail_id: int,
    payload: CocktailUpdate,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    values = payload.model_dump(exclude_unset=True)
    if "name" in values and values["name"] is not None:
        values["name"] = values["name"].strip()
    if "description" in values and values["description"] is not None:
        values["description"] = values["description"].strip()
    if "category" in values and values["category"] is not None:
        values["category"] = values["category"].strip()
    if "instructions" in values and values["instructions"] is not None:
        values["instructions"] = values["instructions"].strip()
    _apply_payload(row, values)
    db.commit()
    db.refresh(row)
    return _serialize(row)


@router.delete("/{cocktail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cocktail(
    cocktail_id: int,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    if (row.image or "").startswith("/uploads/"):
        filename = Path(row.image).name
        if filename and filename != row.image:
            (UPLOAD_DIR / filename).unlink(missing_ok=True)
    db.delete(row)
    db.commit()
