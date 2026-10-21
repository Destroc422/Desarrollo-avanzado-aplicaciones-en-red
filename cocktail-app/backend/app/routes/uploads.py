from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..auth import require_staff
from ..core.config import UPLOAD_DIR
from ..database.session import get_db
from ..models.cocktail import CocktailModel
from ..models.user import UserModel


router = APIRouter(prefix="/uploads", tags=["uploads"])
MAX_IMAGE_SIZE = 5 * 1024 * 1024
_IMAGE_SIGNATURES = {
    ".jpg": lambda data: data.startswith(b"\xff\xd8\xff"),
    ".jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
    ".png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
    ".gif": lambda data: data.startswith((b"GIF87a", b"GIF89a")),
    ".webp": lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP",
}


@router.post("/cocktail/{cocktail_id}")
async def upload_cocktail_image(
    cocktail_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(CocktailModel).filter(CocktailModel.id == cocktail_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")

    suffix = Path(file.filename or "").suffix.lower()
    signature_check = _IMAGE_SIGNATURES.get(suffix)
    allowed_mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(suffix)
    if not signature_check or file.content_type != allowed_mime:
        raise HTTPException(status_code=415, detail="Usa una imagen JPG, PNG, GIF o WebP válida.")

    data = await file.read(MAX_IMAGE_SIZE + 1)
    await file.close()
    if not data or len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="La imagen debe pesar como máximo 5 MB.")
    if not signature_check(data):
        raise HTTPException(status_code=415, detail="El contenido del archivo no coincide con una imagen permitida.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = uuid4().hex + suffix
    target = UPLOAD_DIR / filename
    target.write_bytes(data)
    old_image = row.image or ""
    row.image = "/uploads/" + filename
    try:
        db.commit()
    except Exception:
        db.rollback()
        target.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="No fue posible guardar la imagen.")
    if old_image.startswith("/uploads/"):
        old_path = UPLOAD_DIR / Path(old_image).name
        if old_path != target:
            old_path.unlink(missing_ok=True)
    return {"image_url": row.image}
