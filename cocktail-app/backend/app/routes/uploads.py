from fastapi.staticfiles import StaticFiles
import os
import shutil
from fastapi import UploadFile, File, APIRouter, Depends
from sqlalchemy.orm import Session
from .database.session import get_db
from .models.cocktail import CocktailModel
from .auth import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/image/{cocktail_id}")
async def upload_image(cocktail_id: int, file: UploadFile = File(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizamos la URL en el modelo
    db_cocktail = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if db_cocktail:
        db_cocktail.image = f"/uploads/{file.filename}"
        db.commit()
        db.refresh(db_cocktail)
    
    return {"image_url": db_cocktail.image}
