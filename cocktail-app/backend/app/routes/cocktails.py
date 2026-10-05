from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.session import get_db
from ..models.cocktail import CocktailModel
from ..schemas.cocktail import Cocktail, CocktailCreate, CocktailUpdate
from ..auth import get_current_user

router = APIRouter(prefix="/cocktails", tags=["cocktails"])

@router.get("/", response_model=List[Cocktail])
def read_cocktails(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 10,
    name: Optional[str] = None
):
    query = db.query(CocktailModel)
    if name:
        query = query.filter(CocktailModel.name.contains(name))
    
    cocktails = query.offset(skip).limit(limit).all()
    # Convertimos la lista de ingredientes de string a lista
    for c in cocktails:
        c.ingredients = c.ingredients.split(",") if c.ingredients else []
    return cocktails

@router.get("/{cocktail_id}", response_model=Cocktail)
def read_cocktail(cocktail_id: int, db: Session = Depends(get_db)):
    db_cocktail = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if db_cocktail is None:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    
    # Convertimos los ingredientes
    res = Cocktail.from_orm(db_cocktail)
    res.ingredients = db_cocktail.ingredients.split(",") if db_cocktail.ingredients else []
    return res

@router.post("/", response_model=Cocktail)
def create_cocktail(cocktail: CocktailCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cocktail = CocktailModel(
        name=cocktail.name,
        description=cocktail.description,
        ingredients=",".join(cocktail.ingredients),
        image=cocktail.image
    )
    db.add(db_cocktail)
    db.commit()
    db.refresh(db_cocktail)
    
    # Ajustamos la respuesta para que ingredientes sea lista
    res = Cocktail.from_orm(db_cocktail)
    res.ingredients = cocktail.ingredients
    return res

@router.put("/{cocktail_id}", response_model=Cocktail)
def update_cocktail(cocktail_id: int, cocktail: CocktailUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cocktail = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if db_cocktail is None:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    
    for var, value in cocktail.dict(exclude_unset=True).items():
        if var == "ingredients":
            setattr(db_cocktail, var, ",".join(value))
        else:
            setattr(db_cocktail, var, value)
            
    db.commit()
    db.refresh(db_cocktail)
    
    res = Cocktail.from_orm(db_cocktail)
    res.ingredients = db_cocktail.ingredients.split(",") if db_cocktail.ingredients else []
    return res

@router.delete("/{cocktail_id}")
def delete_cocktail(cocktail_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cocktail = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if db_cocktail is None:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    db.delete(db_cocktail)
    db.commit()
    return {"detail": "Cocktail deleted successfully"}
